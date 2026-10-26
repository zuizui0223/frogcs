

var Select2CascadeCounties = ( function(window, $) {

    function Select2CascadeCounties(parent, child, url, select2Options) {
        var afterActions = [];
        var options = select2Options || {};

        // Register functions to be called after cascading data loading done
        this.then = function(callback) {
            afterActions.push(callback);
            return this;
        };

        parent.select2(select2Options).on("change", function (e) {
			// counties
            child.prop("disabled", true);
            var _this = this;
			var StateCode = $(this).val();
            
			var newurl = url.replace(':statecode:', StateCode);
            $.getJSON(newurl, function(items) {
                var newOptions = '<option value="">-Select-</option>';
                
				items.forEach(function(item) {				
                    newOptions += '<option value="'+ item.CountyFP +'">'+ item.CountyName +'</option>';
                });

                child.select2('destroy').html(newOptions).prop("disabled", false)
                    .select2(options);
                
                afterActions.forEach(function (callback) {
                    callback(parent, child, items);
                });
            });
			
			// species 
			var speciesURL = '../scripts/select2.php?ddl=species&statecode=' + StateCode;
			getSpecies(speciesURL);
			
			// update URL to species export button
			if (StateCode != "") 
			{
				//console.log("update export url" + StateCode);
				$("#downloadSpecies").html(function() {
					return "<a href='../phpspreadsheet/export.php?statecode=" + StateCode + "'><i class='fa fa-download'></i> Download Species List</a>*";
				});
			}
			else
			{
				$("#downloadSpecies").html(function() {
					return "";
				});
				// console.log("hide download button");
				// $("#btnDownload").hide();
				
			}
        });
    }

    return Select2CascadeCounties;

})( window, $);

$("#ddlCounties").on("change", function() {
	var CountyFP = $(this).val();
	var speciesURL = "../scripts/select2.php?ddl=species&statecode=" + $("#ddlStates").val() + "&countyfp=" + CountyFP;	
	getSpecies(speciesURL);
	
	// update URL to species export button
	//console.log("update export url");
	$("#downloadSpecies").html(function() {
		return "<a href='../phpspreadsheet/export.php?statecode=" + $("#ddlStates").val() + "&countyfp=" + CountyFP + "'><i class='fa fa-download'></i>  Download Species List</a>*";
	});
});

function getSpecies(url) 
{	
	$('#ddlSpecies').html("");
	$('#ddlSpecies').select2( {
		theme: 'bootstrap4',
		placeholder: {
			id: '-1', // the value of the option
			text: '-Select-'
		},
		ajax: {
			url: url,
			dataType: 'json',
			data: function (params) {
				var queryParameters = {
					q: params.term
				}

				return queryParameters;
			},
			delay: 250, // wait 250 milliseconds before triggering the request
			complete: function() {
				
			}
		},
	});
	
	// also hide the download species boundary button
	$("#btnDownload").hide();
}