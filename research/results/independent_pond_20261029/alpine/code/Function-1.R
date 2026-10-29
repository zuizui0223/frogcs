## Data list
create_data.list<-function(data,occ.covs_2,method4, session4,coords)
{
  data2 <- data %>% pivot_longer(cols = 2:ncol(data), names_pattern="(.+)") %>% extract(name, c("stade", "espece", "session"), regex = "(.+)_(.+)_(.+)")
  y <- xtabs(value ~ espece + Site + interaction(stade, session), data = data2)
  class(y) <- "array"
  y <- (y>0.5)*1
  
  rownames(occ.covs_2) <- occ.covs_2$Site
  occ.covs<-occ.covs_2[,c(2:54)]
  
  rownames(method4) <- method4$Site
  method4<-method4[,c(2:5)]
  stade=method4
  stade[,c(1:4)] <- lapply(stade, function(x) factor(x, levels = c("Sub_Adult","Adult","eDNA")))
  
  rownames(session4) <- session4$Site
  session4<-session4[,c(2:5)]
  session=session4
  session[,c(1:4)] <- lapply(session, function(x) factor(x, levels = c("Session1", "Session2")))
  
  det.covs<-list(stade=as.list(stade),
                 session=as.list(session))
  
  mytab=coords
  coords=as.matrix(mytab[,2:3])
  dimnames(coords)=list(mytab[,1],names(mytab)[2:3])
  
  data.list <- list(y = y, 
                    occ.covs = occ.covs,
                    det.covs = det.covs, 
                    coords = coords)
  return(data.list)
}

## Models

create_models<-function(EchNb, data.list, path_model="D:/MSOM/modeles/")
  
{
  nl <- which(boucle$N==EchNb)
  for (i in nl){
    
    form1 <- sprintf("~ %s", boucle[i,4])
    form1 <- as.formula(form1)
    form2 <- sprintf("~ %s", boucle[i,6])
    form2 <- as.formula(form2)
    
    mod <- sfMsPGOcc(occ.formula = form1 , 
                     det.formula = form2, 
                     data = data.list,
                     inits = inits.list, 
                     n.batch = n.batch, 
                     batch.length = batch.length, 
                     accept.rate = 0.43, 
                     priors = prior.list, 
                     cov.model = "exponential", 
                     tuning = tuning.list, 
                     n.omp.threads = 1, 
                     verbose = TRUE, 
                     NNGP = TRUE, 
                     n.neighbors = 15, 
                     n.factors = n.factors,
                     search.type = 'cb', 
                     n.report = 10, 
                     n.burn = 2000, 
                     n.thin = 4, 
                     n.chains = 4
    )
    save(mod, file = sprintf("%s/modele_%03d_74.Rdata", path_model, i))
    cat("Modele _ : " , i, "\n")
    rm(mod)
  }
}

