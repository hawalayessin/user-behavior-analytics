# Graphe overfitting - Regression Logistique

Le graphe `logistic_regression_overfitting_curve.png` compare le ROC-AUC obtenu sur l'ensemble d'entrainement et sur l'ensemble de validation pour plusieurs tailles d'apprentissage.

Resultat principal:

- ROC-AUC train final: 0.6126
- ROC-AUC validation final: 0.6132
- Ecart final train-validation: -0.0006
- Ecart maximal observe: 0.0093

Interpretation pour le rapport:

Les courbes train et validation restent proches lorsque la taille d'entrainement augmente. L'ecart de generalisation reste faible, ce qui indique que la regression logistique ne memorise pas excessivement les donnees d'apprentissage. Le modele presente donc une bonne stabilite et constitue un choix pertinent lorsque l'objectif du PFE est de combiner performance, robustesse et interpretabilite.

Mise en valeur de la regression logistique:

La regression logistique offre une interpretabilite forte: ses coefficients permettent d'expliquer directement l'influence des variables churn comme l'inactivite recente, les echecs de paiement ou la retention D7. Meme si Random Forest obtient le meilleur ROC-AUC pur, la regression logistique reste plus facile a justifier devant un jury et plus transparente pour une integration metier.
