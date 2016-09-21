
function reloadTree() {
$('.sortable').nestedSortable({
            handle: 'div',
            items: 'li',
            toleranceElement: '> div',
            listType: 'ul',
            disableNesting: 'hub',
            rootID: 'rootHub',
            protectRoot: true,
            delay: 150,
            placeholder: "ui-state-highlight",
            revert: 250,
            opacity: 0.7,
            helper: "clone",
            handle: "a",
            distance: 4,
//            containment: '.sortable',

            update: function (event, ui) {
                group_id = ui.item.parent().parent().children('div').attr('id');
                children_arr = [];
                ui.item.parent().children().each(function (i) {
                    $(this).children('div').attr("data-order_id", i);
                    children_arr[i] = {id: $(this).children('div').attr("id"),
                                       order_id: i,
                                       type: $(this).attr('class')
                                       };
                });
                $("#modal-wait").show();
                $.post( "/api/reorder", {access_token: localStorage.getItem("atol_access_token"),
                                parent_id: group_id,
                                children: children_arr,
                                },
                    function(response,textStatus,xhr){
                        if (xhr.status == 401){
                            signOut();
                        }
                        if (response.success == true){
                        console.log("success");
                        }
                        else {
                        $('.sortable').nestedSortable("cancel");
                        };
                    $("#modal-wait").hide();
                    },
                'json' ).fail(function() {
                        $("#modal-wait").hide();
                        $('.sortable').nestedSortable("cancel");
                        });
                },

    });
}


function openMenu() {
    $('#open-menu').toggle('fast');

}


function getUserInfo() {
$("#modal-wait").show();
// getUserInfo
    $.get( "/api/get_user_info", {access_token: localStorage.getItem("atol_access_token")},
        function(response,textStatus,xhr){
                if (xhr.status == 401){
                    signOut();
                }
            if (response.success == true){
                $('.body-title').append(response.name);
                //response.type
            }
            else {
            window.open("signin.html","_self");
            };
            $("#modal-wait").hide();
        },
    'json' ).fail(function() {
        $("#modal-wait").hide();
//        $("#main").css("display","none");
        window.open("signin.html","_self");
  });

}


function getTree() {
$("#modal-wait").show();
    $.get( "/api/get_tree", {access_token: localStorage.getItem("atol_access_token")},
        function(response,textStatus,xhr){
                if (xhr.status == 401){
                    signOut();
                }
            if (response.success == true){
                    data = response.tree;
                    $("#rootHub > div > a").html(data.name);
                    $("#rootHub > div").attr("id",data.id);
                    $("#rootHub > div").attr("data-hub_num",data.hub_num);
                    $("#rootHub > div").attr("data-group_num",data.group_num);
                    $('#dashboard-group').html(data.name);
                    localStorage.setItem("rootId", data.id);
                    var children = data.children.sort(function(a, b) {
                      return a.order_id - b.order_id  ||  a.name.localeCompare(b.name);
                    });
                    for (var i = 0; i < children.length; i++) {
                            if (children[i].type == "hub")
                                $("#rootHub > ul").append(
                                    "<li class='hub'><div id='"+children[i].id+"' data-order_id='"+children[i].order_id+"'><i class='fa fa-laptop fa-fw'></i>&nbsp;<a>"+children[i].name+"</a></div></li>"
                                );
                            else
                            if (children[i].type == "group")
                                $("#rootHub > ul").append(
                                    parseTree(children[i])
                                );
                    }
            }
            else {
            };
            function parseTree(elem){
                var children = elem.children.sort(function(a, b) {
                return a.order_id - b.order_id  ||  a.name.localeCompare(b.name);
                });
                var s = "<li class='tab'><div id = '"+elem.id+"' data-hub_num='"+elem.hub_num+"' data-group_num='"+elem.group_num+"' data-order_id='"+elem.order_id+"'><i class='fa fa-fw fa-folder' style='display:none;'></i><i class='fa fa-fw fa-folder-open'></i>&nbsp;<a>";
                s = s + elem.name + "</a></div><ul>";
                for (var i = 0; i < children.length; i++) {
                    console.log(children[i].id);
                        if (children[i].type == "hub")
                            s = s + "<li class='hub'><div id='"+children[i].id+"' data-order_id='"+children[i].order_id+"'><i class='fa fa-laptop fa-fw'></i>&nbsp;<a>"+children[i].name+"</a></div></li>";
                        else
                        if (children[i].type == "group")
                            s = s + parseTree(children[i]);
                }
                return (s + "</ul></li>");
            }
         $("#modal-wait").hide();
        },
    dataType='JSON' ).fail(function() {
        $("#modal-wait").hide();
  }).done(function(){
    $('#group_stats1 > b').text($('.active-elem').attr("data-group_num"));
    $('#group_stats2 > b').text($('.active-elem').attr("data-hub_num"));
  });
}


function addGroup(){
    $("#modal-wait").show();
    order = $('.active-elem').closest('li').children('ul').children('li').last().children('div').attr("data-order_id")+1;
    if (isNaN(order))
        order = 0;
    console.log(order);
    $.post( "/api/create_group", {access_token: localStorage.getItem("atol_access_token"),
                                name: $("#group-form input[name='name']").val(),
                                parent_id: $('.active-elem').attr('id'),
                                order_id: order
                                },
        function(response,textStatus,xhr){
                if (xhr.status == 401){
                    signOut();
                }
            if (response.success == true){
                $('.active-elem').parent().children("ul").append(
                "<li class='tab'><div id = '"+response.id+"' data-order_id='"+order+"'><i class='fa fa-fw fa-folder' style='display:none;'></i><i class='fa fa-fw fa-folder-open'></i>&nbsp;<a>"+response.name+"</a></div><ul></ul></li>"
                );
                $("#group-form input[name='device_id']").val('');
                $("#group-form input[name='name']").val('');
                $("#modal-group").hide();
                reloadTree();
                //response.type
            }
            else {

            };
            $("#modal-wait").hide();
        },
    'json' ).fail(function() {
            $("#modal-wait").hide();
            });
}


function addHub(){
//access_token, device_id, name, group_id
    $("#modal-wait").show();
    order = $('.active-elem').closest('li').children('ul').children('li').last().children('div').attr("data-order_id")+1;
    if (isNaN(order))
        order = 0;
    $.post( "/api/connect_hub", {access_token: localStorage.getItem("atol_access_token"),
                                device_id: $("#hub-form input[name='device_id']").val(),
                                name: $("#hub-form input[name='name']").val(),
                                group_id: $('.active-elem').attr('id'),
                                order_id: order
                                },
        function(response,textStatus,xhr){
                if (xhr.status == 401){
                    signOut();
                }
            if (response.success == true){
                $('.active-elem').parent().children("ul").append(
                "<li class='hub'><div id='"+response.id+"' data-order_id='"+order+"'><i class='fa fa-laptop fa-fw'></i>&nbsp;<a>"+response.name+"</a></div></li>"
                );
                $("#hub-form input[name='device_id']").val('');
                $("#hub-form input[name='name']").val('');
                $("#hub-label").html("Введите идентификатор Хаба");
                $("#modal-hub").hide();
                reloadTree();
                //response.type
            }
            else {
                $("#hub-form input[name='device_id']").val('');
                $("#hub-label").html("Неправильный идентификатор. Введите другой идентификатор Хаба");
            };
            $("#modal-wait").hide();
        },
    'json' ).fail(function() {
                $("#modal-wait").hide();
                $("#hub-form input[name='device_id']").val('');
                $("#hub-label").html("Ошибка. Введите другой идентификатор Хаба");
            });
}


function deleteGroup(){
$("#modal-wait").show();
    $.post( "/api/remove_group", {access_token: localStorage.getItem("atol_access_token"),
                                group_id: $('.active-elem').attr('id')
                                },
        function(response,textStatus,xhr){
                if (xhr.status == 401){
                    signOut();
                }
            if (response.success == true){
                el = $('.active-elem').closest('ul').parent().children('div');
                $('.active-elem').closest('li').remove();
                el.addClass("active-elem");
                $("#modal-delete-group").hide();
                if (el.hasClass('tab-root')) {
                    $('#panel-group').show("fast");
                    $('#panel-hub').show("fast");
                    $('#panel-rename-group').show("fast");
                    $('#panel-rename-hub').hide("fast");
                    $('#panel-delete-hub').hide("fast");
                    $('#panel-delete-group').hide("fast");
                }
                else{
                    $('#panel-group').show();
                    $('#panel-hub').show();
                    $('#panel-rename-group').show();
                    $('#panel-rename-hub').hide();
                    $('#panel-delete-hub').hide();
                    $('#panel-delete-group').show();
                }
                $('#dashboard-hub').hide();
                $('#dashboard-group').show();
                $('#dashboard-group').html(el.children("a").html());
                //response.type
            }
            else {

            };
            $("#modal-wait").hide();
        },
    'json' ).fail(function() {
            $("#modal-wait").hide();
            });
}


function deleteHub(){
    $("#modal-wait").show();
    $.post( "/api/disconnect_hub", {access_token: localStorage.getItem("atol_access_token"),
                                hub_id: $('.active-elem').attr('id'),
                                group_id: $('.active-elem').closest('ul').parent().children('div').attr('id')
                                },
        function(response,textStatus,xhr){
                if (xhr.status == 401){
                    signOut();
                }
            if (response.success == true){
                el = $('.active-elem').closest('ul').parent().children('div');
                $('.active-elem').closest('li').remove();
                el.addClass("active-elem");
                $("#modal-delete-hub").hide();
                $('#panel-group').show();
                $('#panel-hub').show();
                $('#panel-rename-group').show();
                $('#panel-rename-hub').hide();
                $('#panel-delete-hub').hide();
                $('#panel-delete-group').show();

                $('#dashboard-group').show();
                $('#dashboard-group').html(el.children("a").html());
                $('#dashboard-hub').hide();
                //response.type
                $("#modal-wait").hide();
            }
            else {

            };
        },
    'json' ).fail(function() {
            $("#modal-wait").hide();
            });
}


function renameGroup(){
    $("#modal-wait").show();
    $.post( "/api/rename_group", {access_token: localStorage.getItem("atol_access_token"),
                                group_id: $('.active-elem').attr('id'),
                                name: $("#rename-form-group input[name='name']").val(),
                                },
        function(response,textStatus,xhr){
                if (xhr.status == 401){
                    signOut();
                }
            if (response.success == true){
                $('.active-elem > a').html(response.name);
                $("#rename-form-group input[name='name']").val('');
                $("#modal-rename-group").hide();
                reloadTree();
                //response.type
            }
            else {

            };
            $("#modal-wait").hide();
        },
    'json' ).fail(function() {
            $("#modal-wait").hide();
            });

}


function renameHub(){
    $("#modal-wait").show();
    $.post( "/api/rename_hub", {access_token: localStorage.getItem("atol_access_token"),
                                hub_id: $('.active-elem').attr('id'),
                                name: $("#rename-form-hub input[name='name']").val()
                                },
        function(response,textStatus,xhr){
                if (xhr.status == 401){
                    signOut();
                }
            if (response.success == true){
                $('.active-elem > a').html(response.name);
                $("#rename-form-hub input[name='name']").val('');
                $("#modal-rename-hub").hide();
                reloadTree();
                //response.type
            }
            else {

            };
            $("#modal-wait").hide();
        },
    'json' ).fail(function() {
            $("#modal-wait").hide();
            });

}

var TimeoutId = 1;

if (!Array.prototype.last){
    Array.prototype.last = function(){
        return this[this.length - 1];
    };
};

function getSmallHubStatistics(){
    clearTimeout(TimeoutId);
    if ($('.active-elem').parent().hasClass("hub")){
        $.get( "/api/hub_statistics", {access_token: localStorage.getItem("atol_access_token"),
                                    hub_id: $('.active-elem').attr('id')
                                    },
            function(response,textStatus,xhr){
                if (xhr.status == 401){
                    signOut();
                }
                if (response.success == true){
                    $('span[id^=hub_stats]').removeClass('w3-text-green w3-text-red w3-text-dark-grey');

                    $('#hub_stats1 > b').text(response.data.utm_version[0]);
                    $('#hub_stats1').addClass('w3-text-'+response.data.utm_version[1]);

                    $('#hub_stats2 > b').text(response.data.utm_status[0]);
                    $('#hub_stats2').addClass('w3-text-'+response.data.utm_status[1]);

                    $('#hub_stats3 > b').text(response.data.certificate_gost_date[0]);
                    $('#hub_stats3').addClass('w3-text-'+response.data.certificate_gost_date[1]);

                    $('#hub_stats4 > b').text(response.data.certificate_rsa_date[0]);
                    $('#hub_stats4').addClass('w3-text-'+response.data.certificate_rsa_date[1]);

                    $('#hub_stats5 > b').text(response.data.total_tickets_count[0]);
                    $('#hub_stats5').addClass('w3-text-'+response.data.total_tickets_count[1]);

                    $('#hub_stats6 > b').text(response.data.unset_tickets_count[0]);
                    $('#hub_stats6').addClass('w3-text-'+response.data.unset_tickets_count[1]);

                    $('#hub_stats7 > b').text(response.data.buffer_age[0]);
                    $('#hub_stats7').addClass('w3-text-'+response.data.buffer_age[1]);

                    $('#hub_stats8 > b').text(response.data.retail_buffer_size[0]);
                    $('#hub_stats8').addClass('w3-text-'+response.data.retail_buffer_size[1]);

                    $('#status').text(moment(response.data.time).format('DD.MM.YY kk:mm:ss'));
                    //response.type

                    if (myChart !== undefined && myChart.data.labels.last() !== moment(response.data.time)){
                        myChart.data.labels.push(moment(response.data.time));
                        myChart.data.datasets[0].data.push(response.data.utm_status[2]);
                        }

                    if (myChart1 !== undefined && myChart1.data.labels.last() !== moment(response.data.time)){
                        myChart1.data.labels.push(moment(response.data.time));
                        myChart1.data.datasets[0].data.push(response.data.total_tickets_count[0]);
                        myChart1.update();
                        }

                    if (myChart2 !== undefined && myChart2.data.labels.last() !== moment(response.data.time)){
                        myChart2.data.labels.push(moment(response.data.time));
                        myChart2.data.datasets[1].data.push(response.data.unset_tickets_count[0]);//документы
                        myChart2.data.datasets[0].data.push(response.data.retail_buffer_size[0]);//чеки
                        myChart2.update();
                    }
                    ChartsColors();
                    TimeoutId = setTimeout(function(){getSmallHubStatistics();}, 270000);
                }
                else {
                    $("#hub_stats").hide();
                    $("#no_stats").show();
                };
            },
        'json' ).fail(function() {
                    $("#hub_stats").hide();
                    $("#no_stats").show();
                });
    }

}

function ChartsColors() {
    if (myChart !== undefined){
        if (myChart.data.datasets[0].data.last() == 1){
            myChart.data.datasets[0].backgroundColor = 'rgba(50, 100, 0, 0.2)';
            myChart.data.datasets[0].borderColor = 'rgba(50, 100, 0, 1)';
        }
        else if (myChart.data.datasets[0].data.last() == 0){
            myChart.data.datasets[0].backgroundColor = 'rgba(255, 0, 0, 0.2)';
            myChart.data.datasets[0].borderColor = 'rgba(255, 0, 0, 1)';
        }
        else {
            myChart.data.datasets[0].backgroundColor = 'rgba(99, 99, 99, 0.2)';
            myChart.data.datasets[0].borderColor = 'rgba(99, 99, 99, 1)';
        }
        myChart.update();

        if (isNaN(myChart1.data.datasets[0].data.last())){
            myChart1.data.datasets[0].backgroundColor = 'rgba(99, 99, 99, 0.2)';
            myChart1.data.datasets[0].borderColor = 'rgba(99, 99, 99, 1)';
        }
        else {
            myChart1.data.datasets[0].backgroundColor = 'rgba(50, 100, 0, 0.2)';
            myChart1.data.datasets[0].borderColor = 'rgba(50, 100, 0, 1)';
        }
        myChart1.update();

        if ($('#hub_stats7').hasClass('w3-text-green')){
            myChart2.data.datasets[0].backgroundColor = 'rgba(50, 100, 0, 0.2)';
            myChart2.data.datasets[0].borderColor = 'rgba(50, 100, 0, 1)';
        }
        else if ($('#hub_stats7').hasClass('w3-text-red')){
            myChart2.data.datasets[0].backgroundColor = 'rgba(255, 0, 0, 0.2)';
            myChart2.data.datasets[0].borderColor = 'rgba(255, 0, 0, 1)';
        }
        else {
            myChart2.data.datasets[0].backgroundColor = 'rgba(99, 99, 99, 0.2)';
            myChart2.data.datasets[0].borderColor = 'rgba(99, 99, 99, 1)';
        }
        myChart2.update();
    }
}

var myChart; //Статус УТМ
var myChart1; //Количество отправленных документов
var myChart2; //Размер буффера чеков/неотправленных документов

function reloadCharts(period){
    if ($('.active-elem').parent().hasClass("hub")){
        $.get( "/api/charts_statistics", {access_token: localStorage.getItem("atol_access_token"),
                                    hub_id: $('.active-elem').attr('id'),
                                    period: period
                                    },
            function(response,textStatus,xhr){
                if (xhr.status == 401){
                    signOut();
                }
                if (response.success == true){

                    if (myChart !== undefined){
                        myChart.destroy();
                        myChart1.destroy();
                        myChart2.destroy();
                    }
                    var lbls = Array.from(response.data.total_tickets_count.times, x => moment(x));
                    var vls = response.data.total_tickets_count.values;
                    var ctx = document.getElementById("myChart1");
                    myChart1 = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: lbls,
                            datasets: [{
                                lineTension: 0.1,
                                label: 'Количество отправленных документов',
                                pointRadius: 0,
                                pointHitRadius: 10,

                                data: vls,
                                backgroundColor:
                                    'rgba(0, 0, 0, 0.2)'

                                ,
                                borderColor:
                                    'rgba(0, 0, 0, 1)'

                                ,
                                borderWidth: 1
                            }]
                        },
                        options: {
                            scales: {
                                yAxes: [{

                                }],
                                xAxes: [{
                                    type: 'time',
                                    time: {
                                      displayFormats: {
                                       second: 'DD.MM.YY kk:mm:ss',
                                        minute: 'DD.MM.YY kk:mm',
                                        hour: 'DD.MM.YY kk:mm',
                                        day: 'DD.MM.YY',
                                        month: 'DD.MM.YY',
                                        year: 'YYYY'
                                      }
                                        }
                                    }]
                            }
                        }
                    });

                    var lbls = Array.from(response.data.utm_status.times, x => moment(x));
                    var vls = response.data.utm_status.values;
                    var ctx = document.getElementById("myChart");
                    myChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: lbls,
                            datasets: [{
                                steppedLine: true,
                                label: 'Статус УТМ',
                                pointRadius: 0,
                                pointHitRadius: 10,
                                data: vls,
                                backgroundColor:
                                    'rgba(0, 255, 0, 0.2)'

                                ,
                                borderColor:
                                    'rgba(0, 255, 0, 1)'

                                ,
                                borderWidth: 1
                            },
                            ]
                        },
                        options: {
                            scales: {
                                yAxes: [{
                                       stacked: true
                                }],
                                xAxes: [{
                                    type: 'time',
                                    time: {
                                      displayFormats: {
                                        second: 'DD.MM.YY kk:mm:ss',
                                        minute: 'DD.MM.YY kk:mm',
                                        hour: 'DD.MM.YY kk:mm',
                                        day: 'DD.MM.YY',
                                        month: 'DD.MM.YY',
                                        year: 'YYYY'
                                      }
                                        }
                                    }]
                            }
                        }
                    });


                    var lbls = Array.from(response.data.unset_tickets_checks_count.times, x => moment(x));
                    var vls1 = response.data.unset_tickets_checks_count.tickets;
                    var vls2 = response.data.unset_tickets_checks_count.checks;
                    var ctx = document.getElementById("myChart2");
                    myChart2 = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: lbls,
                            datasets: [
                            {
                                lineTension: 0.1,
                                label: 'Размер буффера чеков',
                                pointRadius: 0,
                                pointHitRadius: 10,
                                data: vls2,
                                backgroundColor:
                                    'rgba(255, 0, 0, 0.2)'

                                ,
                                borderColor:
                                    'rgba(255, 0, 0, 1)'

                                ,
                                borderWidth: 1
                            },
                            {
                                lineTension: 0.1,
                                label: 'Количество неотправленных документов',
                                pointRadius: 0,
                                pointHitRadius: 10,
                                data: vls1,
                                backgroundColor:
                                    'rgba(50, 100, 0, 0.2)'

                                ,
                                borderColor:
                                    'rgba(50, 200, 0, 1)'

                                ,
                                borderWidth: 1
                            }]
                        },
                        options: {
                            scales: {
                                yAxes: [{

                                }],
                                xAxes: [{
                                    type: 'time',
                                    time: {
                                      displayFormats: {
                                        second: 'DD.MM.YY kk:mm:ss',
                                        minute: 'DD.MM.YY kk:mm',
                                        hour: 'DD.MM.YY kk:mm',
                                        day: 'DD.MM.YY',
                                        month: 'DD.MM.YY',
                                        year: 'YYYY'
                                      }
                                        }
                                    }]
                            }
                        }
                    });

                ChartsColors();

                    //response.type
                }
                else {

                };
            },
        'json' ).fail(function() {
                });
    }

}