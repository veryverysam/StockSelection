library(psych)
# Read the Stock Features and Manager's Perference from CSV Files
perference = read.csv(file="c:/temp/perference_1.csv", header=TRUE, sep=",")
sec = read.csv(file="c:/temp/secFeatures_1.csv", header=TRUE, sep=",")

#################################
#  Analysis on Perference Table #
#################################

# Run PCA on perference and find out the important component
pca = prcomp(perference, center=TRUE)
summary(pca)

#####################################
#  Analysis on Stock Features Table #
#####################################

# Set Index as cusip
rownames(sec) = sec$cusip
sec$cusip = NULLL
sec$Market.Cap = sec$Market.Cap / 1000000

#Remove rows with missing values and keep only complete cases
final_sec = sec[complete.cases(sec),]

# Create the correlation matrix from data
sec_cor = cor(final_sec)

# Factor analsysi of the data
factors_data = fa(r = sec_cor, nfactors = 5)

# Getting the factor loadings and model analysis
factors_data

# Retrieve the factor loading
print(factors_data$loadings,cutoff=0.3)

