Identifiant pérenne: DOI à créer

Date de publication: 08/07/2024

Titre: Increased drying threatens alpine pond biodiversity more than temperature increase in a changing climate

Autorat : Lamouille-Hébert, Marie (FNE Haute-Savoie, INRAE, Pole ECLA) – ORCID : 0000-0001-9433-7170

Personne-ressource: Lamouille-Hébert, Marie (FNE Haute-Savoie, INRAE, Pole ECLA), marie.hebert@fne-aura.org

Description: 

Data repository for ‘Increased drying threatens alpine pond biodiversity more than temperature increase in a changing climate’
Prepared by Marie Lamouille-Hébert (marie.hebert@fne-aura.org)
1. Overview and background ----------------------------------------------------------
This documentation describes the input data associated with the analysis presented in: Lamouille-Hébert, M., Arthaud, F., Besnard, A., Logez, M, Datry, T. (in prep). Increased drying threatens alpine pond biodiversity more than temperature increase in a changing climate.

Abstract
Climate change is one of the main drivers of species erosion. Rapidly changing climate in the form of warming, drying, and habitat isolation causes freshwater species to change their spatial extent, as most species have little capacity for in situ responses. However, the relative contribution of these three effects to freshwater species’ changing spatial distributions is largely debated. To shed light on this debate, we explored temperature, hydroperiod, and habitat connectivity effects on alpine pond species occupancy probabilities in the Northern French Alps. We studied alpine ponds as ideal test systems because they face climate change effects more rapidly, and in more concentrated areas, than any other freshwater ecosystem. We used multi-species occupancy models with three biological groups (amphibians, macrophytes and Odonata) to examine contrasted responses to climate change. Contrary to expectations, temperature was not the main driver of species occupancy probabilities. Instead, hydroperiod and connectivity were stronger predictors of species occupancy probabilities. Furthermore, temperature increase had the same effect on occupancy probabilities of generalist and cold-specialist species. Nonetheless, temperature disproportionately affected a greater number of specialist species compared to generalists. We conclude that climate change mitigation will primarily benefit a greater number of specialist species than generalists. Finally, we suggest that enhancing our understanding of freshwater hydroperiods will improve our predictions of climate change effects on freshwater species distributions.

The data repository includes data required to perform this analysis. Input data were provided by M, L-H field measurements (detection_non-detection of species, drying gradient observed, temperature data sensors - Hobo, TidbiT-MXTemps400) and analysis (with Quantum Gis (version 3.16.3-Hannover) or RStudio version 2023.5.0.335 (Posit team, 2023) and R version 4.2.0 (R Core Team, 2022). Rosalie Bruel and Adrien Guerou helped to formalize thermal data and provide usable satellite data respectively. We also used the departmental inventory of wetlands made in 2021 by Haute-Savoie territorial department directory (DDT74) and the local conservatory (Asters-CEN74).
All scripts necessary to reproduce this analysis are freely available for all purposes (and can be copied, modified and distributed) in this repository.

2. Repository content ----------------------------------------------------------
The data repository has the following structure:
---------------------------------------------------------code/
Main_script.R: principal script to reproduce this analysis
Function.R: functions script linked with the “Main_script.R”

---------------------------------------------------------data/
Scenari.csv: The list of 104 models created and utilized to run the script
N_58/coords.csv: the coordinates of the 58 ponds where there is data on the following covariates: number of dry days and temperatures
method4.csv: the different methods employed for species detection across the 58 ponds
occ.cov_2.csv: the values of the different covariates across the 58 ponds: number of dry days and temperature covariates
session4.csv: the temporal replicates employed for species detection across the 58 ponds
TableAnalyse_RNN74_Odo_Amphi_Macrophytes_sitesOK.csv: the species detection-non-detection matrix for the 58 sampled ponds.
N_59/coords.csv: the coordinates of the 59 ponds where there is data on the following covariates: number of ice days 
method4.csv: the different methods employed for species detection across the 59 ponds
occ.cov_2.csv: the values of the different covariates across the 59 ponds: number of ice days
session4.csv: the temporal replicates employed for species detection across the 59 ponds
TableAnalyse_RNN74_Odo_Amphi_Macrophytes_sitesOK.csv: the species detection-non-detection matrix for the 59 sampled ponds.
N_73/coords.csv: the coordinates of the 73 ponds where there is data on the following covariates: connectivity covariates and drying gradient
method4.csv: the different methods employed for species detection across the 73 ponds
occ.cov_2.csv: the values of the different covariates across the 73 ponds: connectivity and drying gradient
session4.csv: the temporal replicates employed for species detection across the 73 ponds
TableAnalyse_RNN74_Odo_Amphi_Macrophytes_sitesOK.csv: the species detection-non-detection matrix for the 73 sampled ponds.

----------------------------------------------------------

README_Technical_documentation_CCeffectsonAP_LamouilleHebertetal2024.pdf : documentation for this repository

3. Data format and projection ----------------------------------------------------------
All coordinates are provided in geographic (latitude/longitude) projection, referenced to datum Reseau Geodesique Francais 1993. In ESRI® software this projection is defined by the geographic coordinate system GCS_RGF93_Lambert_93 and datum D_ RGF93_Lambert_93 _EPSG: 2154.

4. License and citations ----------------------------------------------------------
4.1 License agreementThis documentation and datasets are licensed under a Creative Commons Attribution-ShareAlike 4.0 International License (CC-BY-NC 4.0 Deed License). For all regulations regarding license grants, copyright, redistribution restrictions, required attributions, disclaimer of warranty, indemnification, liability, waiver of damages, and a precise definition of licensed materials, please refer to the License Agreement (https://creativecommons.org/licenses/by-nc/4.0/deed.fr). 
4.2 Citations and acknowledgements.Citations and acknowledgements of this dataset should be made as follows: Lamouille-Hébert, M., Arthaud, F., Besnard, A., Logez, M, Datry, T. (in prep). Drying threatens alpine pond biodiversity more than warming in a changing climate. 
We kindly ask users to cite this study in any published material produced using it. If possible, online links to this repository (DOI) should also be provided. 

Sujet: Ecology and conservation

Mot-clé: conservation
freshwater
distribution
models
occupancy
connectivity

Publication connexe: Lamouille-Hébert, M., Arthaud, F., Besnard, A., Logez, M, Datry, T. (in prep). Increased drying threatens alpine pond biodiversity more than temperature increase in a changing climate. 

Dépôt par: Lamouille-Hébert, Marie

Date de dépôt: 2024-07-08