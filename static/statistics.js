document.addEventListener('DOMContentLoaded', function(){
    const zoneFilter=document.getElementById('zones')
    const areaFilter=document.getElementById('areas')
    const allTotal=document.getElementById('totalAll')

    $('#day').addClass('one');
    $('#week').addClass('whites');
    $('#month').addClass('whites');
    $('#months').addClass('whites');
    document.getElementById('over').textContent='Statistics over last 24hours';

    $('#zone_btn').addClass('one');
    $('#area_btn').addClass('whites');

    const area_btn=document.getElementById('area_btn')
    const zone_btn=document.getElementById('zone_btn')
    const target_btn=document.getElementById('zone_btn')
    const target_value=document.getElementById('zone_btn')
    fetchComparisons("zone")
 



    const day_btn=document.getElementById('day')
    const week_btn=document.getElementById('week')
    const month_btn=document.getElementById('month')
    var identi=""





    document.getElementById('save-target').addEventListener('click', function(event){
        event.preventDefault();
       
        var targetValue = document.getElementById('target_text').value.trim();
        var areaName = document.getElementById('areas').value; // Ensure 'areaFilter' is the correct ID

        // Check if the area is 'all'
        if (areaName === 'all') {
            alert('Please select a specific area.');
            return; // Exit the function if 'all' is selected
        }

        if (!areaName) {
            alert('Please select an area.');
            return; // Exit the function if no area is selected
        }

        if (targetValue) {
            setTarget(targetValue, areaName);
        } else {
            alert('Please enter a target value.');
        }

        function setTarget(targetValue, areaName) {
            $.ajax({
                type: 'POST',
                url: '/set_target',
                data: { target_value: targetValue, area_name: areaName },
                success: function(response) {
                   alert(areaName + ' Target value set');
                    fetchStatistics("", areaName, "area");
                }
            });
        }
});



    area_btn.addEventListener('click', function(){
        document.getElementById('comp_text').textContent='Member populations across Areas';
        $('#zone_btn').removeClass('one');
        $('#area_btn').removeClass('whites');
        $('#area_btn').addClass('one');
        $('#zone_btn').addClass('whites');
        fetchComparisons("area")
    });

    zone_btn.addEventListener('click', function(){
        document.getElementById('comp_text').textContent='Member populations across Zones';
        $('#area_btn').removeClass('one');
        $('#zone_btn').removeClass('whites');
        $('#zone_btn').addClass('one');
        $('#area_btn').addClass('whites');
        fetchComparisons("zone")
    });





    day_btn.addEventListener('click', function(){
    document.getElementById('over').textContent='Statistics over last 24hours';
    $('#week').removeClass('one');
    $('#month').removeClass('one');
    $('#months').removeClass('one');
    $('#day').removeClass('whites');
    $('#day').addClass('one');
    $('#week').addClass('whites');
    $('#month').addClass('whites');
    $('#months').addClass('whites');






    var zone_name_filter=zoneFilter.value
    var area_name_filter=areaFilter.value
        if (zone_name_filter=='all'){
            identi="all";
            fetchTimeStats(identi,"24h","","")
        }
        else if(area_name_filter=='all'){
            identi="zone";
            fetchTimeStats(identi,"24h",zone_name_filter,"")
        }
        else if(area_name_filter !='all'){
            identi="area";
            fetchTimeStats(identi,"24h","",area_name_filter)
        }

    });

    week_btn.addEventListener('click', function(){
        $('#day').removeClass('one');
        $('#month').removeClass('one');
        $('#months').removeClass('one');
        $('#week').removeClass('whites');
        $('#week').addClass('one');
        $('#day').addClass('whites');
        $('#month').addClass('whites');
        $('#months').addClass('whites');
    document.getElementById('over').textContent='Statistics over last 7days';


        var zone_name_filter=zoneFilter.value
       var area_name_filter=areaFilter.value
        if (zone_name_filter=='all'){
            identi="all";
            fetchTimeStats(identi,"7d","","")
        }
        else if(area_name_filter=='all'){
            identi="zone";
            fetchTimeStats(identi,"7d",zone_name_filter,"")
        }
        else if(area_name_filter !='all'){
            identi="area";
            fetchTimeStats(identi,"7d","",area_name_filter)
        }
    });

     month_btn.addEventListener('click', function(){
        $('#day').removeClass('one');
        $('#week').removeClass('one');
        $('#months').removeClass('one');
        $('#month').removeClass('whites');
        $('#month').addClass('one');
        $('#day').addClass('whites');
        $('#week').addClass('whites');
        $('#months').addClass('whites');
    document.getElementById('over').textContent='Statistics over last 30days';



        var zone_name_filter=zoneFilter.value
    var area_name_filter=areaFilter.value
        if (zone_name_filter=='all'){
            identi="all";
            fetchTimeStats(identi,"1m","","")
        }
        else if(area_name_filter=='all'){
            identi="zone";
            fetchTimeStats(identi,"1m",zone_name_filter,"")
        }
        else if(area_name_filter !='all'){
            identi="area";
            fetchTimeStats(identi,"1m","",area_name_filter)
        }
    });


    let chart;
    let chartTwo;

    fetch('/get_zones').then(response=>response.json()).then(zones=>{
            zones.forEach(zone=>{
                const option =document.createElement('option');
                option.value=zone;
                option.textContent=zone;
                zoneFilter.appendChild(option);
            });
            zoneFilter.dispatchEvent(new Event('change'));
            fetchStatistics('','','all');
            fetchTimeStats('all','24h','','');
    document.getElementById('over').textContent='Statistics over last 24hours';


            
        });

        zoneFilter.addEventListener('change',function(){
            $('#week').removeClass('one');
            $('#month').removeClass('one');
            $('#months').removeClass('one');
            $('#day').removeClass('whites');
            $('#day').addClass('one');
            $('#week').addClass('whites');
            $('#month').addClass('whites');
            $('#months').addClass('whites');
            const selectedZone=zoneFilter.value;
            
            fetchAreas(selectedZone);
            fetchStatistics(selectedZone,'','zone');
            fetchTimeStats('zone','24h',selectedZone,'');
    document.getElementById('over').textContent='Statistics over last 24hours';



        });
        areaFilter.addEventListener('change',function(){
            $('#week').removeClass('one');
            $('#month').removeClass('one');
            $('#months').removeClass('one');
            $('#day').removeClass('whites');
            $('#day').addClass('one');
            $('#week').addClass('whites');
            $('#month').addClass('whites');
            $('#months').addClass('whites');
            const selectedZone=zoneFilter.value;
            const selectedArea=areaFilter.value;
            fetchStatistics(selectedZone,selectedArea,'area');
            fetchTimeStats('area','24h',selectedZone,selectedArea);
    document.getElementById('over').textContent='Statistics over last 24hours';


        });

        
        async function fetchComparisons(identifier){
            const response=await fetch('/get_comparisons',{
                method:'POST',
                headers:{
                    'Content-Type':'application/json'
                },
                body:
                JSON.stringify({identifier})
            });
            const areas=await response.json();
            $('#comparisons-container').empty();
            generateComparisonChart(areas.area_name,areas.member_count)
        }



        async function fetchAreas(zone){
            const response=await fetch('/get_areas',{
                method:'POST',
                headers:{
                    'Content-Type':'application/json'
                },
                body:
                JSON.stringify({zone})
            });



            const areas=await response.json();
            areaFilter.innerHTML='<option value="all">Select Area</option>';
            
            areas.forEach(area=>{
                const option=document.createElement('option');
                option.value="";
                option.textContent="";
                option.value=area;
                option.textContent=area;
                areaFilter.appendChild(option);
            });
            areaFilter.disabled=false;
        }

        async function fetchStatistics(zone, area, identifier) {
            console.log('fetchStatistics called with:', { zone, area, identifier });
        
            if (zone === 'all') {
                identifier = 'all';
            }
        
            try {
                const response = await fetch('/get_statistics', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ zone, area, identifier })
                });
        
                console.log('Response status:', response.status);
                const data = await response.json();
                console.log('Response data:', data);
        
                if (chart) {
                    chart.destroy();
                }
                $('#don-container').empty();
        
                if (data.members_count > 0) {
                    const male_rate = (data.males_count / data.members_count) * 100;
                    const female_rate = (data.females_count / data.members_count) * 100;
        
                    generateDonutChart(male_rate, female_rate);
                    updateAges(data.age_a, data.age_b, data.age_c, data.members_count,data.target_count);
                } else {
                    updateAges(0, 0, 0, 1, data.target_count);
                }
            } catch (error) {
                console.error('Error fetching statistics:', error);
            }
        }

        
        async function fetchTimeStats(identifier,time_interval,zone_name,area_name){
            if (zone_name=='all'){
                identifier="all";
            }
            const response=await fetch('/get_data',{
                method:'POST',
                headers:{
                    'Content-Type':'application/json'
                },
                body:JSON.stringify({identifier,time_interval,zone_name,area_name})
            });

            const data=await response.json();

            if(chartTwo){
                chartTwo.destroy();
            }
            $('#line-container').empty();
            generateLineChart(data.hours,data.counts)
           
        }









        
        function updateAges(age_a,age_b,age_c,members_count,target_count){
            var age_a_rate=(age_a/members_count)  *100;
            var age_b_rate=(age_b/members_count)  *100;
            var age_c_rate=(age_c/members_count)  *100;
            var to_target=0

            if (members_count>0){
            to_target=(members_count/target_count) *100;
            }
            else{
                to_target=0
            }

            

            document.getElementById('group_a').style.width=age_a_rate + '%';
            document.getElementById('age_text_a').textContent='18-35 Years: ' + Math.round(age_a_rate) + '% (' + age_a +')';
            document.getElementById('total_all').textContent='Total members: ' + members_count;



            document.getElementById('group_b').style.width=age_b_rate + '%';
            document.getElementById('age_text_b').textContent='36-55 Years: ' + Math.round(age_b_rate) + '% (' + age_b +')';

            document.getElementById('group_c').style.width=age_c_rate + '%';
            document.getElementById('age_text_c').textContent='56+ Years: ' + Math.round(age_c_rate) + '% (' + age_c +')';
            document.getElementById('target_all').textContent='Target: ' + target_count;



        }


        function generateDonutChart(male_rate,female_rate){
            document.getElementById('male_text').textContent=Math.round(male_rate) + '% Male';
            document.getElementById('female_text').textContent=Math.round(female_rate) + '% Female';

        var $chartContainer=$('<div>').appendTo('#don-container');
        var $canvas=$('<canvas>').appendTo($chartContainer);
        var ctx=$canvas[0].getContext('2d');
        var chart=new Chart(ctx,{
            type:'doughnut',
            data:{
                labels:['Female','Male'],
                datasets:[{
                    data:[female_rate,male_rate],
                    backgroundColor:[
                        'rgb(255, 0, 0,0.4)',
                        'rgba(255, 0, 0)'

                    ]
                }]
            },
            options:{
                plugins:{
                    tooltip:{
                        enabled:true
                    },
                    legend:{
                        display:true
                    }

                },
                cutout:'60%',
                responsive:true,
                maintainAspectRatio:false
            }
        });

        }

        function generateLineChart(time_frame,count){
           //var lables=[10,20,30,21,63,82,10,20,30,21,63,10,20,30,21,63,82,10,20,30,21,63,82,10,20,30,21,63,82,10,20,30,21,63,82,82,10,20,30,21,63,82,10,20,30,21,63,82];
           //var data=[10,20,30,21,63,82,10,20,30,21,63,10,20,30,21,63,82,10,20,30,21,63,82,10,20,30,21,63,82,10,20,30,21,63,82,82,10,20,30,21,63,82,10,20,30,21,63,82];
            var $chartContainer=$('<div>').appendTo('#line-container');
            var $canvas=$('<canvas>').appendTo($chartContainer);
            var ctx=$canvas[0].getContext('2d');
            var chartTwo=new Chart(ctx,{
                type:'line',
                data:{
                    labels:time_frame,
                    datasets:[{
                        label:'Registered members',
                        data:count,
                        fill:true,
                        backgroundColor:'rgba(255,0,0,0.5)',
                        borderColor:'rgb(255,0,0)',
                        borderWidth:1,
                        pointRadius:1,
                        tension:0.1,
                        spanGaps:true
                    }]
                },
                options:{
                    
                    plugins:{
                        tooltip:{
                            enabled:true
                        },
                        legend:{
                            display:false
                        },
                        zoom:{
                            
                            zoom:{
                                 enabled:true,
                                mode:'xy',
                                },
                            }
                        },
                     responsive:true,
                    maintainAspectRatio:false
                }
            });
    
            }


            
        function generateComparisonChart(area_name,members_count){
            //var lables=[10,20,30,21,63,82,10,20,30,21,63,10,20,30,21,63,82,10,20,30,21,63,82,10,20,30,21,63,82,10,20,30,21,63,82,82,10,20,30,21,63,82,10,20,30,21,63,82];
            //var data=[10,20,30,21,63,82,10,20,30,21,63,10,20,30,21,63,82,10,20,30,21,63,82,10,20,30,21,63,82,10,20,30,21,63,82,82,10,20,30,21,63,82,10,20,30,21,63,82];
             var $chartContainer=$('<div>').appendTo('#comparisons-container');
             var $canvas=$('<canvas>').appendTo($chartContainer);
             var ctx=$canvas[0].getContext('2d');
             var chartTwo=new Chart(ctx,{
                 type:'bar',
                 data:{
                     labels:area_name,
                     datasets:[{
                         label:'Members count',
                         data:members_count,
                         fill:true,
                         backgroundColor:'rgba(112, 119, 224, 0.769)',
                         borderColor:'rgb(112,119,224)',
                         borderWidth:1,
                         pointRadius:0,
                         tension:0.1,
                         spanGaps:true
                     }]
                 },
                 options:{
                     
                     plugins:{
                         tooltip:{
                             enabled:true
                         },
                         legend:{
                             display:false
                         },
                         zoom:{
                             
                             zoom:{
                                  enabled:true,
                                 mode:'xy',
                                 },
                             }
                         },
                      responsive:true,
                     maintainAspectRatio:false
                 }
             });
     
             }

});
