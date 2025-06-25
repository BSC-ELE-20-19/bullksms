document.addEventListener('DOMContentLoaded', function(){
   
    let chart;
    let chartTwo;
    fetchStatistics('', '', 'all');
    fetchTimeStats('all', '24h', '', '');

    function realTimeStats(){
        fetch('/get_real_time').then(response=> response.json()).then(data=>{
            if(data.members_count>0){
                male_rate=(data.males_count/data.members_count)*100;
                female_rate=(data.females_count/data.members_count)*100;
                updateAges(data.age_a,data.age_b,data.age_c,data.members_count,data.new_members,data.target_count)
           }
           else{
               updateAges(15,12,10,11)
           }
            
        });

    }
    realTimeStats();
    setInterval(realTimeStats, 2000)

        async function fetchStatistics(zone,area,identifier){
            if (zone=='all'){
                identifier="all";
            }
            const response=await fetch('/get_statistics',{
                method:'POST',
                headers:{
                    'Content-Type':'application/json'
                },
                body:JSON.stringify({zone,area,identifier})
            });

            const data=await response.json();

            if(chart){
                chart.destroy();
            }
            $('#don-container').empty();

            if(data.members_count>0){
                 male_rate=(data.males_count/data.members_count)*100;
                 female_rate=(data.females_count/data.members_count)*100;

                 generateDonutChart(male_rate,female_rate)

            }
           
        }
        generateDonutChart(35,65);
        updateAges(10,4,2,11);
        generateLineChart();

        
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

        
        function updateAges(age_a,age_b,age_c,members_count,members_new,all_target){
            var age_a_rate=(age_a/members_count)  *100;
            var age_b_rate=(age_b/members_count)  *100;
            var age_c_rate=(age_c/members_count)  *100;
            let new_members=members_new
            let all_members=members_count
            let before=all_members - new_members
            
            if(before<=0){
                before=1;
            }
            let gr_rate=(new_members/before) *100
            

            document.getElementById('group_a').style.width=age_a_rate + '%';
            document.getElementById('age_text_a').textContent='18-35 Years: ' + Math.round(age_a_rate) + '% (' + age_a +')';
            document.getElementById('total_members').textContent=70;
            document.getElementById('new_members').textContent=53;
            document.getElementById('all_target').textContent=42;
            document.getElementById('growth_rate').textContent=Math.round(gr_rate) + '% +';

            document.getElementById('group_b').style.width=age_b_rate + '%';
            document.getElementById('age_text_b').textContent='36-55 Years: ' + Math.round(age_b_rate) + '% (' + age_b +')';

            document.getElementById('group_c').style.width=age_c_rate + '%';
            document.getElementById('age_text_c').textContent='56+ Years: ' + Math.round(age_c_rate) + '% (' + age_c +')';
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
                    data:[40,60],
                    backgroundColor:[
                        'rgba(153, 204, 51,0.4)',
                        'rgb(153, 204, 51)'

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

        function generateLineChart(){
        var labels = Array.from({ length: 50 }, (_, i) => i + 1);

            var data = [
            50, 54, 58, 62, 66, 67, 67, 66, 68, 70,
            81, 82, 82, 81, 79, 77, 74, 71, 68, 64,
            60, 56, 52, 64, 66, 65, 60, 62, 66, 66,
            67, 68, 70, 70, 71, 72, 73, 74, 75, 77,
            77, 77, 77, 79, 81, 82, 82, 81, 79, 76
            ];
var $chartContainer=$('<div>').appendTo('#line-container');
            var $canvas=$('<canvas>').appendTo($chartContainer);
            var ctx=$canvas[0].getContext('2d');
            var chartTwo=new Chart(ctx,{
                type:'line',
                data:{
                    labels:labels,
                    datasets:[{
                        label:'Registered members',
                        data:data,
                        fill:true,
                        backgroundColor:'rgba(153, 204, 51,0.2)',
                        borderColor:'rgb(153, 204, 51)',
                        borderWidth:1,
                        pointRadius:0.8,
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
