function rh_control(id)
{
    value = document.getElementById(id).value
    $.get('rh_step/', value);
}

function on_off()
{
    $.get('on_off/');
}

function light()
{
    $.get('light/');
}

function timer()
{
    $.get('timer/', function(data, status){
        var parsed = data.split("~~")
        if (parsed[0].length > 0){
            var parsed_data = parsed[0].split(';')
            for (i=0; i<parsed_data.length; i++) {
                var datasplit = parsed_data[i].split(',')
                if (datasplit.length > 2){
                    if (datasplit[0].length > 9){
                        var date = new Date(datasplit[0]);
                    }
                    else{
                        var date = new Date()
                    }   
                    var ktherm = Number(datasplit[1]);
                    var rh = Number(datasplit[2]);
					var amb = Number(datasplit[3]);
					var ict = Number(datasplit[4]);
                    //console.log(x)
                    //console.log(datasplit[0].length)
                    //console.log(y)
                    //console.log(z)
                    window.data.push([date, ktherm, rh, amb, ict]);
                }
            }
            window.g.updateOptions( { 'file': window.data } );
            document.getElementById("dht_data").innerHTML = "Temperature: " + ktherm + " F<br> Humidity: " + rh + "%" + "<br>" + date
        }
	console.log("Timer time")
	console.log(parsed[5])
        window.setTimeout(timer, parsed[5])
    })
}

function click_image()
{
    $.get('image/', function(data, status){
        var parsed = data.split("~~")
        document.getElementById("capture").innerHTML = parsed[3]
    })
}

function get_dht(){
    $.get('timer/', function(data, status){
        var parsed = data.split("~~")
        if (parsed[0].length > 0){
            var parsed_data = parsed[0].split(';')
            for (i=0; i<parsed_data.length; i++) {
                var datasplit = parsed_data[i].split(',')
                if (datasplit.length > 2){
                    if (datasplit[0].length > 6){
                        var x = new Date(datasplit[0]);
                    }
                    else{
                        var x = new Date()
                    }   
                    var y = Number(datasplit[1]);
                    var z = Number(datasplit[2]);
                }
            }
            document.getElementById("dht_data").innerHTML = "Temperature: " + y + " F<br> Humidity: " + z + "%" + "<br>" + x
        }
        window.setTimeout(get_dht, 2000)
    })
}
