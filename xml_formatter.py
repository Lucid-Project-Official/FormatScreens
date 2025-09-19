#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Python intelligente pour modifier le contenu des fichiers XML
avec détection automatique des variables.

Transformations appliquées :
1. Correction automatique de la casse (ex: BGIntelliBlowerNumberStation → BGintelliBlowerNumberStation)
2. Détection automatique des variables à partir de SymVarName
3. Remplacement intelligent de &amp;lt;no variable linked&amp;gt; par les vraies variables
4. Synchronisation automatique entre PvID, balises principales et SymVarName

AVANTAGE : Plus besoin de mapping manuel ! L'application détecte automatiquement 
les variables correctes à partir du contenu SymVarName de chaque bloc.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


class XMLFormatter:
    """Classe pour formater les fichiers XML selon les patterns identifiés."""
    
    def __init__(self):
        self.transformations = {
            # Transformation 1: Correction de la casse
            r'BGIntelliBlowerNumberStation\[': 'BGintelliBlowerNumberStation[',
            
            # Transformation 2: Mapping des variables "no variable linked"
            # Ces mappings sont basés sur l'analyse de votre exemple
        }
        
        # Plus besoin de mapping fixe - détection automatique des variables !

    def backup_file(self, file_path: Path) -> Path:
        """Crée une sauvegarde du fichier original."""
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        shutil.copy2(file_path, backup_path)
        print(f"✓ Sauvegarde créée: {backup_path}")
        return backup_path

    def apply_basic_transformations(self, content: str) -> str:
        """Applique les transformations de base (changements de casse, etc.)."""
        modified_content = content
        
        for pattern, replacement in self.transformations.items():
            modified_content = re.sub(pattern, replacement, modified_content)
            
        return modified_content

    def fix_no_variable_linked(self, content: str) -> str:
        """
        Détecte automatiquement les variables à partir des SymVarName et 
        synchronise les PvID avec les vraies variables.
        """
        modified_content = content
        
        # Approche plus simple : traiter chaque bloc ExpProps individuellement
        # Pattern pour capturer un bloc ExpProps complet
        exp_props_pattern = r'<ExpProps_(\d+)[^>]*>.*?</ExpProps_\1>'
        
        def process_exp_props_block(match):
            full_block = match.group(0)
            
            # Vérifier si ce bloc contient "no variable linked"
            if '&amp;lt;no variable linked&amp;gt;' not in full_block:
                return full_block  # Pas de changement nécessaire
            
            # Extraire la variable de SymVarName
            sym_var_match = re.search(r'<SymVarName>([^<]+)</SymVarName>', full_block)
            
            if sym_var_match:
                sym_var_name = sym_var_match.group(1)
                
                # Si SymVarName contient une vraie variable (pas vide)
                if sym_var_name and sym_var_name.strip():
                    print(f"  🔄 Remplacement 'no variable linked' par: '{sym_var_name}'")
                    
                    # Remplacer toutes les occurrences de "&amp;lt;no variable linked&amp;gt;"
                    modified_block = full_block.replace(
                        '&amp;lt;no variable linked&amp;gt;', 
                        sym_var_name
                    )
                    
                    return modified_block
            
            return full_block  # Retourner inchangé
        
        modified_content = re.sub(exp_props_pattern, process_exp_props_block, modified_content, flags=re.DOTALL)
        
        return modified_content

    def synchronize_variables(self, content: str) -> str:
        """
        Synchronise toutes les variables : si une variable existe dans SymVarName,
        elle doit aussi être présente dans PvID et dans la balise principale.
        """
        modified_content = content
        
        # Pattern pour trouver tous les blocs ExpProps
        pattern = r'<ExpProps_(\d+)[^>]*>.*?<Name>([^<]+)</Name>.*?<ExpPropValue>(.*?)</ExpPropValue>.*?</ExpProps_\1>'
        
        def synchronize_block(match):
            prop_num = match.group(1)
            name = match.group(2)
            exp_prop_value = match.group(3)
            
            # Chercher la variable dans SymVarName
            sym_var_match = re.search(r'<SymVarName>([^<]+)</SymVarName>', exp_prop_value)
            
            if sym_var_match:
                sym_var_name = sym_var_match.group(1)
                
                # Si SymVarName contient une vraie variable (pas vide)
                if sym_var_name and sym_var_name.strip():
                    # Extraire le type de variable (ex: "BackColorVariable2", "Variable", etc.)
                    var_type_match = re.search(r'&lt;(\w+)\s+Ver="1"[^&]*&gt;([^&]*)', exp_prop_value)
                    
                    if var_type_match:
                        var_type = var_type_match.group(1)
                        current_var = var_type_match.group(2)
                        
                        # Si la variable actuelle ne correspond pas à SymVarName
                        if current_var != sym_var_name:
                            print(f"  🔄 Synchronisation {name}: '{current_var}' → '{sym_var_name}'")
                            
                            # Remplacer dans la balise principale
                            new_exp_prop_value = re.sub(
                                r'(&lt;' + re.escape(var_type) + r'\s+Ver="1"[^&]*&gt;)[^&]*',
                                r'\1' + sym_var_name,
                                exp_prop_value
                            )
                            
                            # Remplacer dans PvID
                            new_exp_prop_value = re.sub(
                                r'PvID="[^"]*"',
                                f'PvID="{sym_var_name}"',
                                new_exp_prop_value
                            )
                            
                            return f'<ExpProps_{prop_num} NODE="zenOn(R) embedded object"><Name>{name}</Name><ExpPropValue>{new_exp_prop_value}</ExpPropValue></ExpProps_{prop_num}>'
            
            return match.group(0)  # Retourner inchangé
        
        modified_content = re.sub(pattern, synchronize_block, modified_content, flags=re.DOTALL)
        
        return modified_content

    def format_xml_file(self, file_path: Path) -> bool:
        """
        Formate un fichier XML selon les patterns identifiés.
        
        Args:
            file_path: Chemin vers le fichier XML à formater
            
        Returns:
            bool: True si des modifications ont été apportées, False sinon
        """
        try:
            print(f"\n🔄 Traitement de: {file_path}")
            
            # Lire le contenu du fichier
            with open(file_path, 'r', encoding='utf-16') as f:
                original_content = f.read()
            
            # Créer une sauvegarde
            self.backup_file(file_path)
            
            # Appliquer les transformations
            modified_content = original_content
            
            # 1. Transformations de base (changements de casse)
            modified_content = self.apply_basic_transformations(modified_content)
            
            # 2. Correction des "no variable linked" (détection automatique)
            modified_content = self.fix_no_variable_linked(modified_content)
            
            # 3. Synchronisation générale des variables
            modified_content = self.synchronize_variables(modified_content)
            
            # Vérifier s'il y a eu des changements
            if modified_content != original_content:
                # Écrire le fichier modifié
                with open(file_path, 'w', encoding='utf-16') as f:
                    f.write(modified_content)
                
                print(f"✓ Fichier modifié avec succès: {file_path}")
                return True
            else:
                print(f"ℹ️ Aucune modification nécessaire pour: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors du traitement de {file_path}: {str(e)}")
            return False

    def format_directory(self, directory_path: Path) -> Dict[str, int]:
        """
        Formate tous les fichiers XML dans un répertoire.
        
        Args:
            directory_path: Chemin vers le répertoire contenant les fichiers XML
            
        Returns:
            Dict avec les statistiques de traitement
        """
        stats = {
            'total_files': 0,
            'modified_files': 0,
            'errors': 0
        }
        
        if not directory_path.exists():
            print(f"❌ Le répertoire {directory_path} n'existe pas.")
            return stats
        
        # Trouver tous les fichiers XML
        xml_files = list(directory_path.glob('*.XML')) + list(directory_path.glob('*.xml'))
        
        if not xml_files:
            print(f"ℹ️ Aucun fichier XML trouvé dans {directory_path}")
            return stats
        
        print(f"📁 Traitement du répertoire: {directory_path}")
        print(f"📄 {len(xml_files)} fichier(s) XML trouvé(s)")
        
        for xml_file in xml_files:
            stats['total_files'] += 1
            
            try:
                if self.format_xml_file(xml_file):
                    stats['modified_files'] += 1
            except Exception as e:
                stats['errors'] += 1
                print(f"❌ Erreur avec {xml_file}: {str(e)}")
        
        return stats


def main():
    """Fonction principale de l'application."""
    print("🚀 Démarrage de l'application de formatage XML")
    print("=" * 50)
    
    # Initialiser le formateur
    formatter = XMLFormatter()
    
    # Chemin vers le répertoire ToFormat
    toformat_path = Path("ToFormat")
    
    # Traiter tous les fichiers XML dans ToFormat/
    stats = formatter.format_directory(toformat_path)
    
    # Afficher les résultats
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU TRAITEMENT")
    print("=" * 50)
    print(f"📄 Fichiers traités: {stats['total_files']}")
    print(f"✅ Fichiers modifiés: {stats['modified_files']}")
    print(f"❌ Erreurs: {stats['errors']}")
    
    if stats['modified_files'] > 0:
        print(f"\n✓ {stats['modified_files']} fichier(s) ont été modifiés avec succès.")
        print("💾 Les fichiers originaux ont été sauvegardés avec l'extension .backup")
    
    if stats['errors'] > 0:
        print(f"\n⚠️ {stats['errors']} erreur(s) rencontrée(s). Vérifiez les messages ci-dessus.")
    
    print("\n🎉 Traitement terminé!")


if __name__ == "__main__":
    main()
