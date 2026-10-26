// leaflet map			
var map = L.map('mapDiv', {
	zoomControl: false,
	//fullscreenControl: true,
	//drawControl: true
}).setView([38, -99], 4);

L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community',
	subdomains: 'abcd',
	label: 'Topographic'
}).addTo(map);


L.Control.zoomHome({position: 'topright'}).addTo(map);

var layerGroup = L.featureGroup();
layerGroup.addTo(map);

var itis;
var speciesName;
var layers = new Array();	// store the species boundary layers inside arrays so when users toggle back to an older species, this info is already stored, no need to load new data
var layerLegends = new Array();	// we treat this similarly to layerGroup, it holds a list of species legend items

$("#ddlSpecies").on("change",  function() {	
	var itises = $(this).val().toString();	// used later for the download URLs that takes in csv format "123123,12312312,3213123"
	var speciesData = $('#ddlSpecies').select2('data');
	
	if (speciesData.length > 0)
	{
		if (speciesData.length == 1)	// only 1 species selected
		{
			if (itis != speciesData[0].id)	// new species
			{			
				itis = speciesData[0].id;	
				speciesName = speciesData[0].text;
				layerGroup.clearLayers();	// clear all remaining boundary layers
				$("#legendSpeciesBoundary").html("");	// delete all html children of species legend
			}
			
			if (typeof layers[itis] !== 'undefined') {	// this species layer already exists
				layers[itis].addTo(layerGroup);
				$("#legendSpeciesBoundary").append(layerLegends[itis]);	// add the existing species legend to an array of legend items
				map.fitBounds(layers[itis].getBounds());	// zoom to layer extent
				
			}
			else	// species is new, we fetch it from the db
			{
				map.spin(true);
				
				var color = getRandomColor();			// randomize color
				layers[itis] = getJSONLayerByITIS(itis, color);
				layerLegends[itis] = "<tr id='species" + itis + "'><td><div class='pull-left' style='width: 30px; height: 15px; background-color: " + color + "; padding-top: .2px; margin-right: 1em; border: 1px solid rgba(0, 0, 0, .5); opacity: .7;'></div></td><td>" + speciesName + "</td></tr>";
				
				layers[itis].on('data:loaded', function() {	
					layers[itis].addTo(layerGroup);	// geojsonlayer can be added  to map at any time, but we delay it here so we can call map.hasLayer(geojsonLayer) when user opens modal
					$("#legendSpeciesBoundary").append(layerLegends[itis]);	// add species legend to the div
					
					map.fitBounds(layers[itis].getBounds());	// zoom to layer extent
					map.spin(false);
										
					$("#legendSpeciesBoundary").show();
					$(".collapse").collapse("show");					
				});
			}
			$("#legendSpeciesBoundary").show();
			$(".collapse").collapse("show");
			//getSpeciesReferences(itis);
		}
		else
		{
			layerGroup.clearLayers();
			$("#legendSpeciesBoundary").html("");	// delete all html children of species legend
			
			map.spin(true);
			
			for (var i = 0; i < speciesData.length; i++) 
			{
				itis = speciesData[i].id;
				speciesName = speciesData[i].text;
				//console.log("i = " + i + ", itis = " + itis);
				if (typeof layers[itis] !== 'undefined') {	
					//console.log("This species (" + itis + ") layer already existed, re-add it to map species");			
					layers[itis].addTo(layerGroup);
					$("#legendSpeciesBoundary").append(layerLegends[itis]);	// add species legend to the div
				}
				else
				{					
					var color = getRandomColor();			// randomize color
					layers[itis] = getJSONLayerByITIS(itis, color);
					layerLegends[itis] = "<tr id='species" + itis + "'><td><div class='pull-left' style='width: 30px; height: 15px; background-color: " + color + "; padding-top: .2px; margin-right: 1em; border: 1px solid rgba(0, 0, 0, .5); opacity: .7;'></div></td><td>" + speciesName + "</td></tr>";	
					
					layers[itis].on('data:loaded', function() {
						//console.log("Add species " + itis + " layer to map");	
						layers[itis].addTo(layerGroup);	// geojsonlayer can be added  to map at any time, but we delay it here so we can call map.hasLayer(geojsonLayer) when user opens modal
						$("#legendSpeciesBoundary").append(layerLegends[itis]);	// add species legend to the div
					});
				}
				
				//getSpeciesReferences(itis);
			}
			$("#legendSpeciesBoundary").show();
			$(".collapse").collapse("show");
			map.spin(false);
		}
	
		$("#downloadGeoJSON").attr('href', '../gallery/getSpeciesSpatial.php?download=1&format=geojson&itis=' + itises);
		$("#downloadEsriJSON").attr('href', '../gallery/getSpeciesSpatial.php?download=1&format=esri&itis=' + itises);
		$("#btnDownload").show();
	}
	else
	{
		layerGroup.clearLayers();
		$("#legendSpeciesBoundary").html("");	// delete all html children of species legend
		$("#btnDownload").hide();
		$("#downloadGeoJSON").attr('href', '#');
		$("#downloadEsriJSON").attr('href', '#');		
	}
});

// species richness layer
$('#richness-tab').on('click', function () {
	layerGroup.clearLayers();
	$("#legendSpeciesBoundary").html("");	// delete all html children of species legend
	$("#legendSpeciesBoundary").hide();
	map.setView([38, -99], 2);
	
	if (typeof layers["richness"] !== 'undefined') {	
		//console.log("Add new species (" + itis + ") layer to map");
		layers["richness"].addTo(layerGroup);
		//map.fitBounds(layers["richness"].getBounds());	// zoom to layer extent
	}
	else
	{
		map.spin(true);
		
		var color = getRandomColor();			// randomize color
		//console.log(color);
		layers["richness"] = new L.GeoJSON.AJAX("../uploads/data/geojson/species_richness_per_county.json", {	// getting data from existing json file
			onEachFeature: onEachFeatureRichness
		});
		
		
		
		layers["richness"].on('data:loaded', function() {				
			layers["richness"].addTo(layerGroup);	// geojsonlayer can be added  to map at any time, but we delay it here so we can call map.hasLayer(geojsonLayer) when user opens modal
			map.spin(false);
			
		});
	}
	
	$("#legendRichness").show();
	$(".collapse").collapse("show");
	
});

$('#search-tab').on('click', function () {
	layerGroup.clearLayers();
	$("#ddlStates").val(null).trigger('change');	// only need to do this since it will cascade down to the other 2 ddl's
	map.setView([38, -99], 4);
	$("#legendRichness").hide();
});

// these 2 functions convert any string into a hex color
function hashCode(str) { // java String#hashCode
    var hash = 0;
    for (var i = 0; i < str.length; i++) {
       hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    return hash;
} 

function getRandomColor() {
  var letters = '0123456789ABCDEF';
  var color = '#';
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

function getJSONLayerByITIS(itis, color)
{	
	return new L.GeoJSON.AJAX("../uploads/data/geojson/" + itis + ".json", {	// getting data from existing json file
		onEachFeature: onEachFeature,
		// we used to swap the coords, but now that the geojson file are generated with the coords already swapped, we don't need this code anymore
		// coordsToLatLng: function (coords) {
			// //                    latitude , longitude
			// //return new L.LatLng(coords[1], coords[0]); //Normal behavior
			// return new L.LatLng(coords[0], coords[1]);	// swapping coordinates
		// },
		style: {
			"fillColor": color,
			"weight": 1,
			"opacity": 0.7,
			"color": color,
		}
	});
}

function onEachFeature(feature, layer) {
    if (feature.properties) {
        layer.bindPopup(feature.properties.StateCode + ", " + feature.properties.CountyName + " County");
    }
}

function onEachFeatureRichness(feature, layer) {
		layer
		.bindPopup('<div id="div' + feature.properties.StateFP + feature.properties.CountyFP + '" class="speciesPopup"></div>')
		.setStyle(setRichnessColor(feature.properties.NumOfSpecies))
		.on('click', function() {
			//console.log(feature);
			var params = {
				"statefp": feature.properties.StateFP,
				"countyfp": feature.properties.CountyFP
			};
			//console.log(params);
			var div = document.getElementById('div' + feature.properties.StateFP + feature.properties.CountyFP);
			
			$.ajax({
				data: params,
				url: 'species-richness.php',
				beforeSend: function () {
					$(".sk-wave").show();
				},
				success: function (data) {					
					div.innerHTML = "StateFP: " + feature.properties.StateFP + ", CountyFP: " + feature.properties.CountyFP + "<br />StateCode: " + feature.properties.StateCode + ", County Name: " + feature.properties.CountyName + "<br /><br />County Species:<br />" + buildSpeciesPopup(data);
										
				},
				error: function (xmlHttpRequest, textStatus, errorThrown) {
					console.log(xmlHttpRequest.responseText);
					console.log(textStatus);
					console.log(errorThrown);
					var popupHTML = 'ERROR: unable to retrieve data for species popup';
					console.log(popupHTML);
				},
				complete: function () {
					$(".sk-wave").hide();
				}
			});
		});		
}

function setRichnessColor(numOfSpecies)
{
	//console.log(numOfSpecies);
	if (numOfSpecies < 1)
	{
		return {
			"color": "#fdcf6a",	// rgb(253 207 106)
			"weight": 1,
			"opacity": 0.5,
			"fillOpacity": 0,
		};	
	}
	else if (1 <= numOfSpecies && numOfSpecies <= 2)
	{
		return {
			"weight": 1,		// border, on or off
			"fillColor": "#fbf7ba",
			"fillOpacity": .65,
			"color": "#fdcf6a",	// rgb(251 247 186)			
			"opacity": 0.5	// border opacity
		};
	}
	else if (3 <= numOfSpecies && numOfSpecies  <= 6)
	{
		return {
			"color": "#fdcf6a",	// rgb(253 207 106)
			"weight": 1,
			"opacity": 0.7,
			"fillOpacity": .65
		};
	}
	else if (7 <= numOfSpecies && numOfSpecies  <= 14)
	{
		return {
			"color": "#ef9057",	// rgb(239 144 87)
			"weight": 1,
			"opacity": 0.6,
			"fillOpacity": .65
		};
	}
	else if (15 <= numOfSpecies && numOfSpecies  <= 25)
	{
		return {
			"color": "#df422c",	// rgb(223 66 44)
			"weight": 1,
			"opacity": 0.5,
			"fillOpacity": .65
		};
	}
	else if (26 <= numOfSpecies && numOfSpecies  <= 40)
	{
		return {
			"color": "#a53029",	// rgb(165 48 41)
			"weight": 1,
			"opacity": 1,
			"fillOpacity": .65
		};
	}
	else
	{
		return {
			"color": "#a53029",	// rgb(165 48 41)
			"weight": 1,
			"opacity": 1,
			"fillOpacity": .85
		};	
	}	
}

function buildSpeciesPopup(data)
{	
	var html = '';
	if (data.length > 0) 
	{
		$.each(data, function (index, value) {
			html += '<a href="../gallery/species.php?itis=' + value.ITIS + '" target="_blank">' + value.GenusName + ' ' + value.SpeciesName + ' ' + value.Subspecies + '</a><br />';
		});
	}
	else
	{
		html += 'No species found.';
	}
	return html;
}

// function getSpeciesReferences(itis) {	
	// var params = {
		// "itis": itis,
		// "type": "photo"
	// };
	
	// $.ajax({
		// type: "get",
		// url: '../spatial/map_data_bounds.php',
		// data: params,
		// contentType: "application/json; charset=utf-8",
		// dataType: "json",
		// beforeSend: function () {	
			// console.log("get species photos for " + itis);
		// },
		// success: function (data) {
			// var html = "";
			// if (data.length > 0)
			// {								
				// $.each(data, function (index, item) {
					// html += "<img src='../scripts/image_scale.php?url=../uploads/gallery/" + item.FileName + "&width=80' class='img-responsive' />";
				// });
			// }
			// else
			// {
				// html += "No photos available.";
			// }
			// $("#resultsContainer").html(html);
			// $("#resultsContainer").show();
		// },
		// error: function (xmlHttpRequest, textStatus, errorThrown) {
			// console.log("error!");
			// console.log(xmlHttpRequest.responseText);
			// console.log(textStatus);
			// console.log(errorThrown);
		// },
		// complete: function () {
			
		// }
	// });
// }
		