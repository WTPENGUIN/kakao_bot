var chartLabels = [];
var chartData = [];

$(document).ready(function(e) {	
	$.getJSON("http://118.67.129.197:5000/corona.json", function(data){
	
	// 리스트 초기화(이전 차트의 데이터 삭제)
	chartLabels.length = 0;
	chartData.length = 0;
	// 데이터 삽입
	$.each(data, function(inx, obj){
		chartLabels.push(obj.x);
		chartData.push(obj.y);
	});
	// 차트 제작
	createChart();
        });
});

function createChart() {
	// canvas 요소 얻음
	var ctx = document.getElementById("canvas").getContext("2d");

	// 이전 차트 객체가 있으면 객체 파괴
	if(typeof(LineChart) !== 'undefined') {LineChart.destroy();}
	
	// 차트 제작
	LineChart = Chart.Line(ctx,{
		data : {
			labels : chartLabels,
			datasets : [{
				label : "일일확진자 수",
				backgroundColor : "rgba(2,117,216,0.2)",
				borderColor : "rgba(2,117,216,1)",
				pointRadius : 5,
				pointBackgroundColor : "rgba(2,117,216,1)",
				pointBorderColor : "rgba(255,255,255,0.8)",
				pointHoverRadius : 5,
				pointHoverBackgroundColor : "rgba(2,117,216,1)",
				pointHitRadius : 50,
				pointBorderWidth : 2,
				data : chartData,
                                fill : false,
			}]
		},
		options : {
			responsive : true,
			title : {
				display : true,
				text : '코로나 확진자 수',
			},
			tooltips : {
				mode : 'index',
				intersect : false,
			},
			hover : {
				mode : 'nearest',
				intersect : true,
			},
			scales : {
				xAxes : [{
					display : true,
					scaleLabel : {
						display : true,
						labelString : '날짜',
					},
					ticks : {
						beginAtZero : true
					}
				}],
				yAxes : [{
					display : true,
					scaleLabel : {
						display : true,
						labelString : '일일 확진자',
					},
					ticks : {
						beginAtZero : true
					}
				}]
			}
		}
	})
}
