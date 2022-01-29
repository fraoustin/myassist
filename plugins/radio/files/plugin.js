function del_radio(obj){
    var xmlhttp = new XMLHttpRequest();
    var theUrl = "/api/radio/del";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("radio", obj.id);
    xmlhttp.send(data);
    obj.parentNode.parentNode.parentNode.removeChild(obj.parentNode.parentNode);
}

function add_radio(){
    document.getElementById("addradio").style.display="";
}

function close_radio(){
    document.getElementById("addradio").style.display="none";
}

function save_radio(){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            location.reload();
        };
    };
    var theUrl = "/api/radio/add";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("name", document.getElementById("name").value);
    data.append("url", document.getElementById("url").value);
    xmlhttp.send(data);
    document.getElementById("addradio").style.display="none";
}