# Formateur XML pour zenOn

## Description

Cette application Python modifie automatiquement le contenu des fichiers XML selon la logique identifiée dans les fichiers d'exemple.

## Transformations appliquées

L'application effectue les transformations suivantes :

1. **Correction de casse** : `BGIntelliBlowerNumberStation[1]` → `BGintelliBlowerNumberStation[1]`

2. **Remplacement des variables non liées** : Remplace `&amp;lt;no variable linked&amp;gt;` par les vraies variables :
   - `BarGraph.XVariable` → `BGIntelliBlowerSpace[1]`
   - `OutOfRangeHigh.XVariable` → `BGIntelliBlowerSpace[1]`
   - `NumberStation.VisibilityVariable` → `BGIntelliBlowerVisuPointA[1]`
   - `OutOfRangeDown.XVariable` → `BGIntelliBlowerSpace[1]`
   - `BarGraph.VisibilityVariable` → `BGIntelliBlowerVisuPointA[1]`
   - `NumberStation.XVariable` → `BGIntelliBlowerSpace[1]`

3. **Synchronisation** : Met à jour automatiquement les valeurs `PvID` et `SymVarName` pour qu'elles correspondent.

## Utilisation

### Prérequis
- Python 3.6 ou plus récent

### Exécution
```bash
python xml_formatter.py
```

L'application :
- Traite automatiquement tous les fichiers XML (*.XML, *.xml) dans le dossier `ToFormat/`
- Crée une sauvegarde de chaque fichier original avec l'extension `.backup`
- Affiche un résumé détaillé des modifications effectuées

### Structure des dossiers
```
FormatScreens/
├── xml_formatter.py      # Application principale
├── ToFormat/             # Dossier contenant les fichiers à modifier
│   ├── fichier1.XML
│   ├── fichier2.XML
│   └── ...
└── Example/              # Dossier contenant les fichiers d'exemple
    ├── DEV_BarGraphIntelliBlower.XML
    └── DEV_BarGraphIntelliBlowerModified.XML
```

## Sécurité

- **Sauvegarde automatique** : Tous les fichiers originaux sont sauvegardés avant modification
- **Vérification d'encodage** : Support de l'encodage UTF-16 utilisé par zenOn
- **Gestion d'erreurs** : Affichage détaillé des erreurs et continuation du traitement

## Résultats

L'application affiche :
- ✅ Nombre de fichiers traités et modifiés
- 💾 Confirmation des sauvegardes créées
- ❌ Détail des erreurs éventuelles
- 📊 Résumé complet du traitement
