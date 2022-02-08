function del_wol(obj){
    var xmlhttp = new XMLHttpRequest();
    var theUrl = "/api/wol/del";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("wol", obj.id);
    xmlhttp.send(data);
    obj.parentNode.parentNode.parentNode.removeChild(obj.parentNode.parentNode);
}

function add_wol(){
    document.getElementById("addwol").style.display="";
}

function close_wol(){
    document.getElementById("addwol").style.display="none";
}

function save_wol(){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            location.reload();
        };
    };
    var theUrl = "/api/wol/add";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("name", document.getElementById("name").value);
    data.append("url", document.getElementById("url").value);
    xmlhttp.send(data);
    document.getElementById("addwol").style.display="none";
}