function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
};

function del_timing(obj){
    var xmlhttp = new XMLHttpRequest();
    var theUrl = "/api/timing/del";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("timing", obj.id);
    xmlhttp.send(data);
    obj.parentNode.parentNode.parentNode.removeChild(obj.parentNode.parentNode);
}

function reset_timing(){
    document.getElementById("oldname").value = "";
    document.getElementById("active").value = false;
    document.getElementById("name").value = "";
    document.getElementById("hour").value = "1";
    document.getElementById("minute").value = "0";
    document.getElementById("monday").value = false;
    document.getElementById("tuesday").value = false;
    document.getElementById("wednesday").value = false;
    document.getElementById("thursday").value = false;
    document.getElementById("friday").value = false;
    document.getElementById("saturday").value = false;
    document.getElementById("sunday").value = false;
    Array.from(document.getElementById("table_timing").querySelectorAll("tr.step")).forEach(function(obj){
        obj.parentNode.removeChild(obj)
    });
}

function add_timing(){
    reset_timing();
    document.getElementById("addtiming").style.display="";
}

function close_timing(){
    document.getElementById("addtiming").style.display="none";
}

function save_timing(){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            location.reload();
        };
    };
    var theUrl = "/api/timing/add";
    xmlhttp.open("POST", theUrl);
    var datas = {};
    datas["oldname"] = document.getElementById("oldname").value;
    datas["name"] = document.getElementById("name").value;
    datas["active"] = document.getElementById("active").checked;
    datas["hour"] = document.getElementById("hour").value;
    datas["minute"] = document.getElementById("minute").value;
    datas["monday"] = document.getElementById("monday").checked;
    datas["tuesday"] = document.getElementById("tuesday").checked;
    datas["wednesday"] = document.getElementById("wednesday").checked;
    datas["thursday"] = document.getElementById("thursday").checked;
    datas["friday"] = document.getElementById("friday").checked;
    datas["saturday"] = document.getElementById("saturday").checked;
    datas["sunday"] = document.getElementById("sunday").checked;
    var steps = []
    Array.from(document.getElementById("table_timing").querySelectorAll("tr.step")).forEach(function(obj){
        steps.push(obj.querySelectorAll("input")[0].value)
    });
    datas["steps"] = steps;
    var data = new FormData();
    data.append("timing", JSON.stringify(datas, null, 2))
    xmlhttp.send(data);
    document.getElementById("addtiming").style.display="none";
}

var steptiming = `
<tr class="step">
    <td></td>
    <td><input class="siimple-input siimple-input--fluid" value=""></td>
    <td class="minimal"><div class="siimple-btn--big icon-timing-del siimple--float-right" onclick="del_timing_step(this)"></div></td>
</tr>
`;

function add_timing_step(){
    document.getElementById("table_timing").appendChild(htmlToElement(steptiming));
}

function del_timing_step(obj){
    obj.parentNode.parentNode.parentNode.removeChild(obj.parentNode.parentNode)
}

function view_timing(obj){
    reset_timing();
    var datas = JSON.parse(obj.parentNode.querySelectorAll("td")[2].textContent);
    document.getElementById("oldname").value = datas['name'];
    document.getElementById("name").value = datas['name'];
    document.getElementById("active").checked = datas['active'];
    document.getElementById("hour").value = datas['hour'];
    document.getElementById("minute").value = datas['minute'];
    document.getElementById("monday").checked = datas['monday'];
    document.getElementById("tuesday").checked = datas['tuesday'];
    document.getElementById("wednesday").checked = datas['wednesday'];
    document.getElementById("thursday").checked = datas['thursday'];
    document.getElementById("friday").checked = datas['friday'];
    document.getElementById("saturday").checked = datas['saturday'];
    document.getElementById("sunday").checked = datas['sunday'];
    datas["steps"].forEach(function(step){
        document.getElementById("table_timing").appendChild(htmlToElement(steptiming));        
        document.getElementById("table_timing").querySelectorAll("tr.step:last-child input")[0].value = step;
    });
    document.getElementById("addtiming").style.display="";
}

function change_timing(obj){
    var datas = JSON.parse(obj.parentNode.parentNode.parentNode.querySelectorAll("td")[2].textContent);
    datas['oldname'] = datas['name']
    if ( datas['active'] == true ) {
        datas['active'] = false;
    } else {
        datas['active'] = true;        
    };
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            location.reload();
        };
    };
    var theUrl = "/api/timing/add";
    xmlhttp.open("POST", theUrl);
    var data = new FormData();
    data.append("timing", JSON.stringify(datas, null, 2))
    xmlhttp.send(data);
}