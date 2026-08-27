from typing import TypedDict


class Command(TypedDict):
    software: str
    command: str


class Method(TypedDict):
    id: str
    name: str
    definition: str
    formula: str
    utility: str
    conditions: list[str]
    example: str
    commands: list[Command]


class Module(TypedDict):
    id: str
    name: str
    description: str
    methods: list[Method]


CATALOG: list[Module] = [
    {
        "id": "descriptive",
        "name": "Statistique descriptive",
        "description": "Resumer et explorer les caracteristiques principales des donnees.",
        "methods": [
            {
                "id": "mean",
                "name": "Moyenne",
                "definition": "Somme des observations divisee par le nombre d'observations.",
                "formula": "x_bar = sum(x_i) / n",
                "utility": "Mesurer la tendance centrale d'une variable quantitative.",
                "conditions": ["Variable quantitative", "Observations correctement codees"],
                "example": "Calculer le revenu moyen d'un echantillon de menages.",
                "commands": [
                    {"software": "Stata", "command": "summarize revenu"},
                    {"software": "R", "command": "mean(revenu, na.rm = TRUE)"},
                    {"software": "Python", "command": "df['revenu'].mean()"},
                ],
            },
            {
                "id": "standard_deviation",
                "name": "Ecart-type",
                "definition": "Mesure la dispersion des observations autour de leur moyenne.",
                "formula": "s = sqrt(sum((x_i - x_bar)^2) / (n - 1))",
                "utility": "Quantifier la dispersion dans l'unite de la variable.",
                "conditions": ["Variable quantitative", "Au moins deux observations"],
                "example": "Comparer la dispersion des revenus entre deux echantillons.",
                "commands": [
                    {"software": "Stata", "command": "summarize revenu"},
                    {"software": "R", "command": "sd(revenu, na.rm = TRUE)"},
                    {"software": "Python", "command": "df['revenu'].std()"},
                ],
            },
        ],
    },
    {
        "id": "inference",
        "name": "Statistique inferentielle",
        "description": "Tester des hypotheses et quantifier l'incertitude des resultats.",
        "methods": [
            {
                "id": "ttest",
                "name": "Test t de Student",
                "definition": "Comparer une moyenne observee a une reference ou comparer deux moyennes.",
                "formula": "t = (estimation - reference) / erreur_standard",
                "utility": "Evaluer si une difference de moyennes est compatible avec l'hypothese nulle.",
                "conditions": ["Variable quantitative", "Observations independantes selon le cas", "Hypotheses du test verifiees"],
                "example": "Comparer le revenu moyen d'un echantillon a une valeur de reference.",
                "commands": [
                    {"software": "Stata", "command": "ttest revenu = 1000"},
                    {"software": "R", "command": "t.test(revenu, mu = 1000)"},
                    {"software": "Python", "command": "stats.ttest_1samp(revenu, 1000)"},
                ],
            },
            {
                "id": "anova",
                "name": "ANOVA",
                "definition": "Comparer les moyennes de trois groupes ou plus.",
                "formula": "F = variance inter-groupes / variance intra-groupes",
                "utility": "Determiner si au moins une moyenne de groupe differe.",
                "conditions": ["Variable dependante quantitative", "Facteur qualitatif", "Au moins deux observations par groupe"],
                "example": "Comparer le revenu moyen entre plusieurs regions.",
                "commands": [
                    {"software": "Stata", "command": "oneway revenu region"},
                    {"software": "R", "command": "summary(aov(revenu ~ region, data = df))"},
                    {"software": "Python", "command": "stats.f_oneway(groupe1, groupe2, groupe3)"},
                ],
            },
        ],
    },
    {
        "id": "econometrics",
        "name": "Modeles econometriques",
        "description": "Modeliser des relations et estimer des probabilites.",
        "methods": [
            {
                "id": "ols",
                "name": "Regression lineaire OLS",
                "definition": "Relier une variable dependante quantitative a une ou plusieurs explicatives.",
                "formula": "Y = beta_0 + beta_1 X_1 + ... + beta_k X_k + u",
                "utility": "Estimer une relation moyenne et evaluer sa significativite.",
                "conditions": ["Variable dependante quantitative", "Explicatives quantitatives dans le MVP", "Diagnostics des residus"],
                "example": "Expliquer le revenu par l'age et le niveau d'education.",
                "commands": [
                    {"software": "Stata", "command": "reg revenu age education"},
                    {"software": "R", "command": "lm(revenu ~ age + education, data = df)"},
                    {"software": "Python", "command": "sm.OLS(y, sm.add_constant(X)).fit()"},
                ],
            },
            {
                "id": "logit",
                "name": "Modele Logit",
                "definition": "Modeliser la probabilite d'un evenement binaire.",
                "formula": "P(Y=1|X) = 1 / (1 + exp(-X beta))",
                "utility": "Estimer et classifier une issue codee 0/1.",
                "conditions": ["Cible binaire codee 0/1", "Explicatives quantitatives dans le MVP", "Absence de separation parfaite"],
                "example": "Estimer la probabilite d'adoption d'une technologie.",
                "commands": [
                    {"software": "Stata", "command": "logit adoption age revenu"},
                    {"software": "R", "command": "glm(adoption ~ age + revenu, family = binomial, data = df)"},
                    {"software": "Python", "command": "sm.Logit(y, X).fit()"},
                ],
            },
        ],
    },
]


def all_methods() -> list[Method]:
    return [method for module in CATALOG for method in module["methods"]]


CATALOG[0]["methods"].extend(
    [
        {
            "id": "median",
            "name": "Mediane",
            "definition": "Valeur qui partage les observations ordonnees en deux parties de meme effectif.",
            "formula": "Position centrale des valeurs ordonnees",
            "utility": "Resister aux valeurs extremes et decrire une distribution asymetrique.",
            "conditions": ["Variable quantitative ou ordinale", "Observations ordonnees"],
            "example": "Decrire le revenu central lorsque quelques revenus sont tres eleves.",
            "commands": [
                {"software": "Stata", "command": "summarize revenu, detail"},
                {"software": "R", "command": "median(revenu, na.rm = TRUE)"},
                {"software": "Python", "command": "df['revenu'].median()"},
            ],
        },
        {
            "id": "variance",
            "name": "Variance",
            "definition": "Moyenne des ecarts au carre autour de la moyenne, avec n - 1 pour un echantillon.",
            "formula": "s^2 = sum((x_i - x_bar)^2) / (n - 1)",
            "utility": "Mesurer la dispersion avant de revenir a l'unite originale avec l'ecart-type.",
            "conditions": ["Variable quantitative", "Au moins deux observations"],
            "example": "Quantifier la variabilite des scores d'un groupe d'etudiants.",
            "commands": [
                {"software": "Stata", "command": "summarize score"},
                {"software": "R", "command": "var(score, na.rm = TRUE)"},
                {"software": "Python", "command": "df['score'].var()"},
            ],
        },
        {
            "id": "coefficient_of_variation",
            "name": "Coefficient de variation",
            "definition": "Rapport entre l'ecart-type et la moyenne, exprime en pourcentage.",
            "formula": "CV = (s / x_bar) * 100",
            "utility": "Comparer la dispersion relative de variables d'echelles differentes.",
            "conditions": ["Variable quantitative positive de preference", "Moyenne non nulle"],
            "example": "Comparer la variabilite relative de deux indicateurs economiques.",
            "commands": [
                {"software": "Stata", "command": "summarize x"},
                {"software": "R", "command": "sd(x, na.rm = TRUE) / mean(x, na.rm = TRUE) * 100"},
                {"software": "Python", "command": "df['x'].std() / df['x'].mean() * 100"},
            ],
        },
        {
            "id": "mode",
            "name": "Mode",
            "definition": "Valeur ou categorie la plus frequente dans les observations.",
            "formula": "Frequence maximale",
            "utility": "Identifier la valeur la plus courante, y compris pour une variable categorielle.",
            "conditions": ["Variable quantitative ou categorielle", "Plusieurs modes possibles"],
            "example": "Identifier la region ou le niveau d'education le plus represente.",
            "commands": [
                {"software": "Stata", "command": "tabulate region"},
                {"software": "R", "command": "names(sort(table(region), decreasing = TRUE))[1]"},
                {"software": "Python", "command": "df['region'].mode()"},
            ],
        },
    ]
)

CATALOG[1]["methods"].extend(
    [
        {
            "id": "chi_square",
            "name": "Test du Chi-deux",
            "definition": "Tester l'independance entre deux variables qualitatives.",
            "formula": "chi2 = sum((observed - expected)^2 / expected)",
            "utility": "Evaluer une association entre deux variables categorielles.",
            "conditions": ["Deux variables qualitatives", "Effectifs attendus suffisants"],
            "example": "Etudier le lien entre la region et l'adoption d'une technologie.",
            "commands": [
                {"software": "Stata", "command": "tab region adoption, chi2"},
                {"software": "R", "command": "chisq.test(table(df$region, df$adoption))"},
                {"software": "Python", "command": "stats.chi2_contingency(table)"},
            ],
        },
        {
            "id": "fisher",
            "name": "Test exact de Fisher",
            "definition": "Tester une association dans une table de contingence 2x2 a faibles effectifs.",
            "formula": "Probabilite exacte conditionnelle aux marges",
            "utility": "Remplacer le Chi-deux lorsque ses conditions d'effectifs ne sont pas satisfaites.",
            "conditions": ["Deux variables qualitatives", "Table 2x2 dans le MVP", "Faibles effectifs possibles"],
            "example": "Tester une association avec un petit echantillon.",
            "commands": [
                {"software": "R", "command": "fisher.test(table(df$x, df$y))"},
                {"software": "Python", "command": "stats.fisher_exact(table)"},
            ],
        },
        {
            "id": "vif",
            "name": "Facteur d'inflation de la variance",
            "definition": "Mesure la collinearite d'une variable explicative avec les autres explicatives.",
            "formula": "VIF_j = 1 / (1 - R_j^2)",
            "utility": "Detecter une dependance lineaire qui rend les coefficients instables.",
            "conditions": ["Modele avec plusieurs explicatives", "Variables quantitatives dans le MVP"],
            "example": "Verifier que age et anciennete n'apportent pas une information redondante.",
            "commands": [
                {"software": "Stata", "command": "estat vif"},
                {"software": "R", "command": "car::vif(model)"},
                {"software": "Python", "command": "variance_inflation_factor(X, i)"},
            ],
        },
        {
            "id": "breusch_pagan",
            "name": "Test de Breusch-Pagan",
            "definition": "Tester si la variance des erreurs d'une regression est constante.",
            "formula": "LM = n * R^2 du modele auxiliaire",
            "utility": "Diagnostiquer l'heteroscedasticite et envisager des erreurs standards robustes.",
            "conditions": ["Modele lineaire estime", "Residus et variables explicatives disponibles"],
            "example": "Verifier si la dispersion des erreurs augmente avec le revenu predit.",
            "commands": [
                {"software": "Stata", "command": "estat hettest"},
                {"software": "R", "command": "lmtest::bptest(model)"},
                {"software": "Python", "command": "het_breuschpagan(model.resid, model.model.exog)"},
            ],
        },
    ]
)

CATALOG[2]["methods"].append(
    {
        "id": "probit",
        "name": "Modele Probit",
        "definition": "Modeliser la probabilite d'une issue binaire avec la fonction de repartition normale.",
        "formula": "P(Y=1|X) = Phi(X beta)",
        "utility": "Estimer une probabilite binaire avec une liaison normale.",
        "conditions": ["Cible binaire codee 0/1", "Explicatives quantitatives dans le MVP", "Absence de separation"],
        "example": "Estimer la probabilite qu'un menage adopte une technologie.",
        "commands": [
            {"software": "Stata", "command": "probit adoption age revenu"},
            {"software": "R", "command": "glm(adoption ~ age + revenu, family = binomial(link = 'probit'), data = df)"},
            {"software": "Python", "command": "sm.Probit(y, X).fit()"},
        ],
    }
)
