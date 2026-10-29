#' Feeding experiments without prey replacement
#'
#' Feeding experiment data from Hossie and Murray (2010) downloaded from the
#' FoRAGE database (Uiterwaal et al. 2022). Eaten prey were not replaced during the
#' experiment. Includes data for a dragonfly nymph predator feeding on tadpoles
#' in three leaf litter treatments.
#'
#' @format A data frame with 91 rows and 6 variables:
#' \describe{
#'   \item{N0}{Number of initial prey}
#'   \item{NE}{Number of eaten prey}
#'   \item{Time}{Duration (h)}
#'   \item{Predator}{Predator species}
#'   \item{Prey}{Prey species}
#'   \item{ID}{Leaf litter treatment}
#' }
#'
#' @source
#'   Hossie T. J. and Murray D. S. (2010).
#'   You can't run but you can hide: refuge use in frog tadpoles elicits density-dependent predation by dragonfly larvae.
#'   *Oecologia*, 163, 395-404.
#'   https://doi.org/10.1007/s00442-010-1568-6
#'
#'   Uiterwaal S. F., Lagerstrom I. T., Lyon S. R., and DeLong, J. P. (2022).
#'   FoRAGE Database: A Compilation of Functional Responses for Consumers and Parasitoids.
#'   *Ecology* 103(7): e3706.
#'   https://doi.org/10.1002/ecy.3706
#'
#'   FoRAGE database V5 (2024).
#'   https://doi.org/10.5063/F1RX99KB
#'
#' @usage data(df_Hossie_and_Murray_2010_OECOLOGIA)
#'
#' @examples
#' data(df_Hossie_and_Murray_2010_OECOLOGIA)
#' head(df_Hossie_and_Murray_2010_OECOLOGIA)
"df_Hossie_and_Murray_2010_OECOLOGIA"
