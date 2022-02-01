function del_alarm(obj){
    var xmlhttp = new XMLHttpRequest();
    var theUrl = "/api/alarm/del";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("alarm", obj.id);
    xmlhttp.send(data);
    obj.parentNode.parentNode.parentNode.removeChild(obj.parentNode.parentNode);
}

function add_alarm(){
    document.getElementById("addalarm").style.display="";
}

function close_alarm(){
    document.getElementById("addalarm").style.display="none";
}

function save_alarm(){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            location.reload();
        };
    };
    var theUrl = "/api/alarm/add";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("name", document.getElementById("name").value);
    data.append("url", document.getElementById("url").value);
    xmlhttp.send(data);
    document.getElementById("addalarm").style.display="none";
}