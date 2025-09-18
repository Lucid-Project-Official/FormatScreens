#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Python pour modifier le contenu des fichiers XML
selon la logique identifiée dans les fichiers d'exemple.

Transformations appliquées :
1. BGIntelliBlowerNumberStation[1] → BGintelliBlowerNumberStation[1] (changement de casse)
2. Remplacement de &amp;lt;no variable linked&amp;gt; par les vraies variables
3. Synchronisation des variables PvID et SymVarName
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
        
        # Mapping des variables pour remplacer "&amp;lt;no variable linked&amp;gt;"
        self.variable_mappings = {
            'BarGraph.XVariable': 'BGIntelliBlowerSpace[1]',
            'OutOfRangeHigh.XVariable': 'BGIntelliBlowerSpace[1]',
            'NumberStation.VisibilityVariable': 'BGIntelliBlowerVisuPointA[1]',
            'OutOfRangeDown.XVariable': 'BGIntelliBlowerSpace[1]',
            'BarGraph.VisibilityVariable': 'BGIntelliBlowerVisuPointA[1]',
            'NumberStation.XVariable': 'BGIntelliBlowerSpace[1]',
        }

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
        Remplace les occurrences de "&amp;lt;no variable linked&amp;gt;" 
        par les vraies variables selon le contexte.
        """
        modified_content = content
        
        # Pattern pour trouver les blocs ExpProps avec "no variable linked"
        pattern = r'<ExpProps_(\d+)[^>]*>.*?<Name>([^<]+)</Name>.*?<ExpPropValue>(.*?)&amp;lt;no variable linked&amp;gt;(.*?)</ExpPropValue>.*?</ExpProps_\1>'
        
        def replace_no_variable(match):
            prop_num = match.group(1)
            name = match.group(2)
            before_var = match.group(3)
            after_var = match.group(4)
            
            # Chercher la variable correspondante dans notre mapping
            if name in self.variable_mappings:
                replacement_var = self.variable_mappings[name]
                
                # Reconstruire le bloc avec la vraie variable
                new_before = before_var.replace('&amp;lt;no variable linked&amp;gt;', replacement_var)
                
                # Mettre à jour aussi le SymVarName si présent
                new_after = re.sub(
                    r'<SymVarName>([^<]*)</SymVarName>',
                    f'<SymVarName>{replacement_var}</SymVarName>',
                    after_var
                )
                
                return f'<ExpProps_{prop_num} NODE="zenOn(R) embedded object"><Name>{name}</Name><ExpPropValue>{new_before}{replacement_var}{new_after}</ExpPropValue></ExpProps_{prop_num}>'
            
            return match.group(0)  # Retourner inchangé si pas de mapping trouvé
        
        modified_content = re.sub(pattern, replace_no_variable, modified_content, flags=re.DOTALL)
        
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
            
            # 1. Transformations de base
            modified_content = self.apply_basic_transformations(modified_content)
            
            # 2. Correction des "no variable linked"
            modified_content = self.fix_no_variable_linked(modified_content)
            
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
