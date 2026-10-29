
#references:
#https://www.jeffdoser.com/files/spoccupancy-web/reference/sfmspgocc
#https://cran.r-project.org/web/packages/spOccupancy/spOccupancy.pdf
#https://www.jeffdoser.com/files/spoccupancy-web/


source("C:/Users/marie.lamouille-hebe/Documents/R/ScriptsCIMaE/spOccupancyRNN74_all/MSOM/function.R")

## Packages
library(tidyverse)
library(spOccupancy)
library(coda)
library(stars)
library(ggplot2)
library(sf)
library(pals)
library(cowplot)
library(MCMCvis)
library(RColorBrewer)


## Data # modified in function of the three different data sets (73, 58, 59)
path_model <- "D:/MSOM/modeles/"
data=read.csv2("~/R/ScriptsCIMaE/spOccupancyRNN74_all/MSOM/data/Inter/TableAnalyse_RNN74_Odo_Amphi_Macrophytes_sitesOK.csv")
occ.covs_2<-read.csv2("~/R/ScriptsCIMaE/spOccupancyRNN74_all/MSOM/data/Inter/occ.cov_2.csv")
method4<-read.csv2("~/R/ScriptsCIMaE/spOccupancyRNN74_all/MSOM/data/Inter/method4.csv")
session4<-read.csv2("~/R/ScriptsCIMaE/spOccupancyRNN74_all/MSOM/data/Inter/session4.csv")
coords<-read.csv2("~/R/ScriptsCIMaE/spOccupancyRNN74_all/MSOM/data/Inter/coords.csv")
boucle<-read.csv(file="~/R/ScriptsCIMaE/spOccupancyRNN74_all/Results/Scenari.csv",header = TRUE,sep = ";")

## Data list
data.list<-create_data.list(data,occ.covs_2,method4,session4,coords)
save(data.list, file="5_Data_list.RData") 
load("C:/Users/marie.lamouille-hebe/Documents/R/ScriptsCIMaE/spOccupancyRNN74_all/MSOM/73_Data_list.Rdata")

## Bayesian indices
prior.list <- list(beta.comm.normal = list(mean = 0, var = 2.72), 
                   alpha.comm.normal = list(mean = 0, var = 2.72), 
                   tau.sq.beta.ig = list(a = 0.1, b = 0.1), 
                   tau.sq.alpha.ig = list(a = 0.1, b = 0.1),
                   phi.unif = list(a = 3/1, b = 3/.1)) 
n.factors=15
N=31
lambda.inits <- matrix(0, N, n.factors)
diag(lambda.inits) <- 1
lambda.inits[lower.tri(lambda.inits)] <- rnorm(sum(lower.tri(lambda.inits)))
inits.list <- list(alpha.comm = 0, 
                   beta.comm = 0, 
                   beta = 0, 
                   alpha = 0,
                   tau.sq.beta = 1, 
                   tau.sq.alpha = 1, 
                   phi = 3 / .5, 
                   lambda = lambda.inits,
                   z = apply(data.list$y, c(1, 2), max, na.rm = TRUE))
n.batch <- 500
batch.length <- 40
n.samples <- n.batch * batch.length
tuning.list <- list(phi = 1) 

##Models
EchNb=73 # modified in function of the three different data sets (73, 58, 59)
path_model <- "D:/MSOM/modeles/"
create_models(EchNb,data.list, path_model)

##Model validations 
path_model <- ("D:/MSOM/modeles")
path_figure<- ("D:/MSOM/figures")
path_table<-("D:/MSOM/tables")

nl <- which(boucle$N==EchNb)
WAIC <- numeric(length(nl))
u<-1
for (i in nl) {
  load(file = sprintf("D:/MSOM/modeles/modele_%03d_74.Rdata",i))
  
  png(file = sprintf("D:/MSOM/figures/Conv_Occ_%03d_74_Occ.png",i), width = 900, height = 1500)
  plot(mod$beta.samples, density = FALSE) # Occupancy parameters.
  dev.off()
  png(file = sprintf("D:/MSOM/figures/Conv_Detect_%03d_74_Det.png",i), width = 900, height = 1500)
  plot(mod$alpha.samples, density = FALSE) # Detection parameters.
  dev.off()
  
  bpval <- function(object) {   
    bpval_comm <- mean(object$fit.y.rep > object$fit.y)
    N <- ncol(object$fit.y)
    bpval_sp <- numeric(N)
    
    for (i in 1:N) {
      bpval_sp[i] <- mean(object$fit.y.rep[, i] > object$fit.y[,i])
    }
    out <- data.frame(Taxa = c("Comm", object$sp.names), p_val = c(bpval_comm, bpval_sp))
    return(out)
  }
  
  test1 <- ppcOcc(mod, 'freeman-tukey', group = 2)
  sum1<- bpval(test1)
  write.table(sum1, 
              sprintf("D:/MSOM/tables/summary_test_1_%03d.csv", i),
              row.names = FALSE, sep=";") 
  
  test2 <- ppcOcc(mod, 'freeman-tukey', group = 1)
  sum2 <- bpval(test2)
  write.table(sum2, 
              sprintf("D:/MSOM/tables/summary_test_2_%03d.csv", i),
              row.names = FALSE, sep=";") 
  
  ##Figures of the significant effect, or not, of the different occ.cov on occupancy probabilities of species
  png(file = sprintf("D:/MSOM/figures/Sp_%03d.png",i), width = 900, height = 1500)
  MCMCplot(mod$beta.samples, ref_ovl = TRUE, ci = c(50, 95))
  dev.off()
  
  WAIC[u]<-waicOcc(mod)[3]
  u<-u+1
  
}

WAIC<-data.frame(nl=nl, WAIC=WAIC)

write.table(WAIC,sprintf("D:/MSOM/tables/WAIC_%d.csv", EchNb),
            row.names = FALSE, sep = ";")

## Predict of the occupancy probabilities of species on the tested variable range (when its effect is significant)
##this part of the script is created by Maxime Logez (2024_01)

extract_names <- function(xnames, deep = TRUE) {
  xnames <- gsub(" +", "", xnames)
  if (any(grepl(":", xnames))){
    xnames <- strsplit(xnames, ":")
    xnames <- sapply(xnames, extract_names)
    xnames <- unlist(xnames)
    xnames <- unique(xnames)
  }else{
    if (any(grepl("^I\\(", xnames))) {
      xnames <- gsub("(?:^I\\()(.+)(?:\\))", "\\1", xnames)
    }
    if (deep){
      while(any(grepl("\\(", xnames))) {
        xnames <- gsub("(?:.*\\()(.+)(?:\\).*)", "\\1", xnames)
      }
      xnames <- unique(xnames)
    }
  }
  xnames
}

extract_intercept <- function(xnames) {
  u <- grepl("Intercept", xnames)
  if (any(u))
    xnames <- xnames[!u]
  xnames
}

simplify_modnames <- function(mod_names) {
  mod_names <- gsub("I\\(scale\\(", "I\\(", mod_names)
  mod_names <- gsub("\\)\\^2", "\\^2", mod_names)
  mod_names <- strsplit(mod_names, ":")
  mod_names <- lapply(mod_names, function(x) gsub("(scale\\()(.+)(\\))", "\\2", x))
  mod_names <- lapply(mod_names, paste, collapse = ":")
  mod_names <- unlist(mod_names)
  mod_names <- sub("\\(Intercept\\)", "Intercept", mod_names)
  mod_names
}

f_inter <- function(x.pred, x.fixed, xvars) {
  inters <- logical(length(x.fixed))
  for (i in 1:length(inters)) {
    test1 <- any(grepl(sprintf("%s(.*)?:(.*)?%s", x.pred, x.fixed[i]), xvars))
    test2 <- any(grepl(sprintf("%s(.*)?:(.*)?%s", x.fixed[i], x.pred), xvars))
    inters[i] <- test1 | test2
  }
  if(all(!inters)){
    inters <- NULL
  }else{
    inters <- x.fixed[inters]
  }
  inters
}

prep_data <- function(x.pred, x.fixed = NULL, inters = NULL, tab) {
  quant_inter <- function(x) {
    if (length(unique(x))<=5) {
      res <- sort(unique(x))
    }else{
      res <- quantile(x, c(0.2, 0.5, 0.8), na.rm = TRUE)  
    }
    res
  }
  
  x.fixed <- setdiff(x.fixed, inters)
  if (is.matrix(tab))
    tab <- as.data.frame(tab)
  if (length(inters) > 0.5){
    inters <- tab[, inters, drop = FALSE]
    inters <- lapply(inters, quant_inter)
  }
  if (length(x.fixed)> 0.5){
    x.fixed <- tab[, x.fixed, drop = FALSE]
    x.fixed <- lapply(x.fixed, mean, na.rm = T)
  }
  x.pred <- tab[, x.pred, drop = FALSE]
  x.pred <- lapply(x.pred, 
                   function(x) seq(min(x, na.rm = TRUE), 
                                   max(x, na.rm = TRUE), le = 101))
  tab <- c(x.pred, inters, x.fixed)
  tab <- do.call(expand.grid, tab)
  tab
}

prep_graph <- function(mod, xnames, x.pred, data = NULL){
  
  xvars <- mod$x.names 
  
  xvars[grep("Intercept", xvars)] <- 1
  form1 <- as.formula(sprintf("~ %s", paste(xvars, collapse = " + ")))
  
  if (is.null(x.pred) || length(x.pred) < 0.5 || is.na(x.pred))
    x.pred <- character()
  
  x.fixed <- xnames[!xnames %in% x.pred]
  if (length(x.fixed) < 0.5)
    x.fixed <- NULL
  if (any(auxi <- grepl("\\:", xvars))) {
    inters <- f_inter(x.pred, x.fixed, xvars)
  }else{
    inters <- NULL
  }
  if (length(inters)> 1.5) {
    stop("Seulement une interaction possible prévue entre\nla variable d'intérêt et les autres")
  }
  
  tab_pred <- prep_data(x.pred, x.fixed, inters, data)
  
  tab_new <- model.matrix(form1, data = tab_pred)
  if (nrow(tab_new) < 0.5) {
    tab_new <- matrix(1L, 1 , 1)
    colnames(tab_new) <- "Intercept"
  }else{
    colnames(tab_new) <- sub("\\(Intercept\\)", "Intercept", colnames(tab_new))
  }
  
  lsp <- colnames(mod$beta.samples)
  lsp <- lsp[grep("Intercept", lsp)]
  lsp <- gsub("\\(Intercept\\)-", "", lsp)
  
  cnames <- colnames(mod$beta.samples)
  linkinv <- binomial()$linkinv
  res <- vector("list", length = length(lsp))
  for (i in 1:length(lsp)) {
    sp <- lsp[i]
    cfs <- mod$beta.samples[, grep(sp, cnames), drop = FALSE]
    cfs <- as.matrix(cfs)
    colnames(cfs) <- gsub(sprintf("-%s", sp), "", colnames(cfs))
    nint <- grep("Intercept", colnames(cfs))
    cfs <- cfs[, c(nint, setdiff(1:ncol(cfs), nint)), drop = FALSE]
    colnames(cfs) <- simplify_modnames(colnames(cfs))
    colnames(cfs)[1] <- "Intercept"
    cfs <- cfs[, colnames(tab_new), drop = FALSE]
    cfs <- t(cfs)
    ps <- tab_new[, , drop = FALSE] %*% cfs[, , drop = FALSE]
    ps <- t(ps)
    int_tot <- apply(ps, 2, quantile, c(0.025, 0.5, 0.975)) #HDI ?
    int_tot <- t(int_tot)
    colnames(int_tot) <- c("pocc_inf", "pocc", "pocc_sup")
    int_tot <- int_tot[, c("pocc", "pocc_inf", "pocc_sup"), drop = FALSE]
    ints <- linkinv(int_tot)
    res[[i]] <- ints
  }
  names(res) <- lsp
  res$tab_new <- tab_new
  res$tab_pred <- tab_pred
  res$lsp <- lsp
  res$inters <- inters # n'existe pas si null
  return(res)
}

graph_var_sp <- function(tab, var1, inter, sp, plot = TRUE) {
  if (length(var1)  < 0.5 || is.na(var1)){
    p1 <- ggplot(tab, aes(x = factor(1), pocc)) +
      geom_linerange(aes(ymin = pocc_inf, ymax = pocc_sup)) + 
      geom_point() +
      xlab("Intercept") + 
      theme_bw() + 
      theme(axis.text.x = element_blank())
  }else{
    var1 <- sym(var1)
    p1 <- ggplot(tab, aes(x = {{var1}}, pocc)) + 
      geom_path() + 
      geom_ribbon(aes(ymin = pocc_inf, ymax = pocc_sup), alpha = 0.5) + 
      theme_bw()
  }
  if (!is.null(inter)) {
    if (is.numeric(tab[, inter]))
      tab[, inter] <- factor(round(tab[, inter], 1))
    p1 <- p1 + facet_wrap(inter, labeller = label_both)
  }
  p1 <- p1 +
    labs(title = {{sp}}) +
    ylab("Occupancy probability") +
    labs(title = {{sp}}) + 
    ylim(0, 1) +
    theme(plot.title = element_text(face = "italic"))
  if (plot){
    plot(p1)
  }else{
    return(p1)
  }
}


graph_var_multi <- function(tab, var1, plot = TRUE, ncol = 3, nrow = round(length(lsp)/3)) {
  auxi <- length(var1)  < 0.5 | is.na(var1)
  if (auxi){
    p1 <- ggplot(tab, aes(x = factor(1), pocc)) +
      geom_linerange(aes(ymin = pocc_inf, ymax = pocc_sup)) + 
      geom_point() +
      xlab("Intercept")
  }else{
    var1 <- sym(var1)
    p1 <- ggplot(tab, aes(x = {{var1}}, pocc)) +
      geom_path() +
      geom_ribbon(aes(ymin = pocc_inf, ymax = pocc_sup), alpha = 0.5)
  }
  p1 <- p1 + 
    facet_wrap(~sp, ncol = ncol) + 
    ylab("Occupancy probability") +
    ylim(0, 1) +
    theme_bw()+ 
    theme(strip.background = element_rect(fill = "white", color = "transparent"),
          strip.text.x.top = element_text(face = "italic"),
          panel.grid.major = element_line(linewidth = 0.2),
          panel.grid.minor = element_line(linewidth = 0.1)
    )
  if(auxi){
    p1 <- p1 +
      theme(axis.text.x = element_blank())
  }  
  if (plot){
    plot(p1)
  }else{
    return(p1)
  }
}

effect_mod <- function(mod, data, path = getwd(), file.name, 
                       tab = "init", gtype = "sp", lsp = NULL,
                       ncol = 3, width = 7, height = 7) {
  
  sp_mod <- gsub("(^.+-)(.+$)", "\\2", colnames(mod$beta.samples))
  sp_mod <- unique(sp_mod)
  if (is.null(lsp)) {
    lsp <- sp_mod
  }else{
    if (!inherits(lsp, "data.frame") || ncol(lsp)!=2) {
      stop("lsp must be a two columns data.frame")
    }
    if (any(!sp_mod %in% lsp$sp_mod)) {
      stop("The species code of lsp must those used in the model (beta.samples)")
    }
    lsp <- lsp$sp[match(sp_mod, lsp$sp_mod)]
  }
  
  mod_names <- mod$x.names 
  xnames <- extract_names(mod_names)
  xnames <- extract_intercept(xnames)
  
  if (length(xnames) > 0.5) {
    scaled <- sapply(xnames, function(x) {
      x <- grep(x, mod_names, value = TRUE)
      x <- x[1]
      res <- grepl("scale", x)
      res
    })
  }else {
    scaled <- FALSE
  }
  
  data_mod <- data
  if (any(scaled)) {
    mns <- colMeans(data[, xnames[scaled], drop = FALSE], na.rm = TRUE)
    sds <- sapply(data[, xnames[scaled], drop = FALSE], sd, na.rm = TRUE)
    for (i in xnames[scaled]) {
      data_mod[, i] <- (data_mod[, i] - mns[i])/sds[i]
    }
    mod_names <- simplify_modnames(mod_names)
    mod$x.names <- mod_names
  }
  
  auxi <- if (length(xnames) < 0.5) 1 else 1:length(xnames)
  pdf(sprintf("%s/%s.pdf", path, file.name),
      width = width, height = height)
  for (i in auxi) { #pour toutes les variables du modèle
    x.pred <- xnames[i]
    tabs <- prep_graph(mod, xnames, x.pred, data_mod)
    if (any(u <- scaled[colnames(tabs$tab_pred)])) {
      tab2 <- tabs$tab_pred
      for (j in colnames(tab2)[u]) {
        tab2[, j] <- tab2[, j]*sds[j]+mns[j]
      }
      tabs$tab_pred <- tab2
      rm(tab2)
    }
    inter <- tabs$inter # nom des variables en interaction avec x.pred
    if (!tab %in% "init"){
      tab1 <- tabs$tab_new
      cn <- colnames(tab1)
      cn <- extract_names(cn, deep = FALSE)
      colnames(tab1) <- cn
      xnames <- cn[grep(x.pred, cn)]
      xnames <- xnames[1]
    }else{
      tab1 <- tabs$tab_pred
    }
    names(tabs)[match(sp_mod, names(tabs))] <- lsp
    if (!is.null(inter) || gtype == "sp") { # graphique par espèce
      for (j in lsp) {
        graph_var_sp(if (nrow(tab1)>0.5) cbind(tab1, as.data.frame(tabs[[j]])) else as.data.frame(tabs[[j]]),
                     x.pred, inter, j, plot = TRUE)
      }
    }else {
      for (j in lsp) {
        if (nrow(tab1 > 0.5)){
          tabs[[j]] <- cbind(tab1, sp = j, as.data.frame(tabs[[j]]))
        }else{
          tabs[[j]] <- cbind(sp = j, as.data.frame(tabs[[j]]))
        }
      }
      tab_m <- do.call(rbind, tabs[lsp])
      graph_var_multi(tab_m, x.pred, plot = TRUE, ncol = ncol)
    }
  }
  dev.off()
}

## Example with a model
load("73_Data_list.Rdata")
d1 <- data.list
load("./graph_effect/modele_002_74.Rdata")
effect_mod(mod, data.list$occ.covs, file.name = "mod_002")
effect_mod(mod, data.list$occ.covs, file.name = "mod_002_m", gtype = "m", ncol = 5,
           height = 10)


