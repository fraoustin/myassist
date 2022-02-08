function del_free(obj){
    var xmlhttp = new XMLHttpRequest();
    var theUrl = "/api/free/del";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("free", obj.id);
    xmlhttp.send(data);
    obj.parentNode.parentNode.parentNode.removeChild(obj.parentNode.parentNode);
}

function add_free(){
    document.getElementById("addfree").style.display="";
}

function close_free(){
    document.getElementById("addfree").style.display="none";
}

function save_free(){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            location.reload();
        };
    };
    var theUrl = "/api/free/add";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("name", document.getElementById("name").value);
    data.append("token", document.getElementById("token").value);
    data.append("id", document.getElementById("id").value);
    xmlhttp.send(data);
    document.getElementById("addfree").style.display="none";
}