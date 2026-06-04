# Conclusion automatique - comparaison churn

Le modele retenu selon le compromis performance / interpretabilite est **Logistic Regression (class_weight/scale_pos_weight)**. Il obtient un ROC-AUC de 0.6093, un F1-score de 0.2541 et une PR-AUC de 0.2600. Ce choix equilibre la qualite de discrimination, la detection de la classe churn et la capacite a expliquer le modele dans un rapport de PFE.

Le meilleur score ROC-AUC est obtenu par **Random Forest (class_weight/scale_pos_weight)** avec 0.7720. Le meilleur F1-score est obtenu par **XGBoost (class_weight/scale_pos_weight)** avec 0.4122.

Analyse par famille de modeles:
- **Logistic Regression**: meilleure variante SMOTE, ROC-AUC=0.6093, F1=0.2541, interpretabilite=Forte. tres interpretable et utile comme baseline robuste, mais peut sous-apprendre les relations non lineaires.
- **Random Forest**: meilleure variante class_weight/scale_pos_weight, ROC-AUC=0.7720, F1=0.4110, interpretabilite=Moyenne. capture des interactions non lineaires et donne des importances de variables, mais reste moins lisible qu'une regression logistique.
- **SVM (RBF)**: meilleure variante class_weight/scale_pos_weight, ROC-AUC=0.6590, F1=0.2693, interpretabilite=Faible. peut modeliser des frontieres complexes avec le noyau RBF, mais son interpretabilite est faible et le cout d'inference peut augmenter.
- **XGBoost**: meilleure variante class_weight/scale_pos_weight, ROC-AUC=0.7682, F1=0.4122, interpretabilite=Moyenne. souvent performant sur donnees tabulaires, avec une bonne gestion des interactions, mais plus complexe a justifier et a regler.

Classement compromis:
1. Logistic Regression (class_weight/scale_pos_weight) - score compromis=0.6658, ROC-AUC=0.6093, F1=0.2541
2. Logistic Regression (SMOTE) - score compromis=0.6572, ROC-AUC=0.6093, F1=0.2541
3. XGBoost (class_weight/scale_pos_weight) - score compromis=0.6485, ROC-AUC=0.7682, F1=0.4122
4. Random Forest (class_weight/scale_pos_weight) - score compromis=0.6387, ROC-AUC=0.7720, F1=0.4110
5. XGBoost (SMOTE) - score compromis=0.6297, ROC-AUC=0.7588, F1=0.3925
6. Random Forest (SMOTE) - score compromis=0.5851, ROC-AUC=0.7717, F1=0.4113
7. SVM (RBF) (class_weight/scale_pos_weight) - score compromis=0.4812, ROC-AUC=0.6590, F1=0.2693
8. SVM (RBF) (SMOTE) - score compromis=0.4744, ROC-AUC=0.6542, F1=0.2529
