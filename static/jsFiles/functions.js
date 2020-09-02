/**
 * 删除指定元素下所有子元素
 * @param id 指定元素的id
 */
function removeAllChild(id) {
    var elem = document.getElementById(id);
    while (elem.hasChildNodes()) {
        elem.removeChild(elem.firstChild);
    }
}

/**
 * 根据参数内容创建一个单位用于显示角色或装备
 * @param unit_id 显示的角色或装备的id，6位数字
 * @param unit_name 角色或装备的名称
 * @param imgType 图片的类型，equipment或unit用于图片文件名
 * @param hasInput 是否添加input元素
 * @param classList 该单位中各个元素的class
 * @returns {HTMLDivElement}
 */
function createUnit(unit_id, unit_name, imgType, hasInput, classList) {
    var unitDiv = document.createElement("div");
    //console.log(classList["unitDiv"]);
    $(unitDiv).addClass(classList["unitDiv"]);
    var unitBox = document.createElement("div");
    $(unitBox).addClass(classList["unitBox"]);

    var img = document.createElement("img");
    img.src = `/static/img/icon_${imgType}_${unit_id}.png`;
    img.title = unit_id;
    $(img).addClass(classList["img"]);
    img.setAttribute("unit_id", unit_id);

    var small = document.createElement("small");
    small.innerHTML = unit_name;
    $(small).addClass(classList["text"]);

    unitBox.appendChild(img);
    unitBox.appendChild(small);

    if (hasInput === true) {
        var input = document.createElement("input");
        input.type = "text";
        $(input).addClass(classList["input"]);
        $(input).val(0);
        unitBox.appendChild(input);
    }

    unitDiv.appendChild(unitBox);

    return unitDiv;
}

/**
 * 用于在网页中添加鼠标选中的角色
 * @param conID 用于显示的容器id
 * @param selectedUnit 被选中的角色信息数组
 */
function drawSelectedUnit(conID, selectedUnit) {
    removeAllChild(conID);
    var container = document.getElementById(conID);
    for (var item of selectedUnit) {
        //console.log(Object.getOwnPropertyNames(item));
        container.appendChild(createUnit(item["equip_id"], item["equip_name"], "unit", false, {
            unitDiv: "col-sm-2",
            unitBox: "unitBox",
            img: "selectedImg",
            text: "label label-default"
        }));
    }
}

/**
 * 在对象数组中查找指定的对象
 * @param list 对象数组
 * @param obj 查找的对象
 * @returns {boolean}
 */
function findObjectInList(list, obj) {
    for (var item of list) {
        if (cmpObject(obj, item)) {
            return true;
        }
    }
    return false;
}

/**
 * 判断两个对象内容是否相同
 * @param cur 需要比较的对象
 * @param tar 被比较的对象
 * @returns {boolean}
 */
function cmpObject(cur, tar) {
    var curKeys = Object.getOwnPropertyNames(cur);
    var tarKeys = Object.getOwnPropertyNames(tar);

    if (curKeys.length !== tarKeys.length) {
        return false;
    }

    for (var key of curKeys) {
        if (!tar.hasOwnProperty(key) || tar[key] !== cur[key]) {
            return false;
        }
    }
    return true;
}

/**
 * 获取指定id的表单数据，并返回包含对应内容的对象
 * @param id 表单id
 */
function getFormParas(id) {
    var formValue = $(`#${id}`).serializeArray();
    var formParas = {};
    for (var i = 0; i < formValue.length; i++) {
        formParas[formValue[i]["name"]] = formValue[i]["value"];
    }
    return formParas;
}

/**
 * 根据获得的表单数据，生成角色rank装备的信息
 * @param formInfo 包含表彰数据的对象
 * @param maxRank 设置的最大rank
 */
function infoProcess(formInfo, maxRank) {
    var res = {};
    if (formInfo.hasOwnProperty("curRank") && formInfo["curRank"] !== "") {
        res["cur_rank"] = parseInt(formInfo["curRank"]);
    } else {
        res["cur_rank"] = 1;
    }
    if (formInfo.hasOwnProperty("tarRank") && formInfo["tarRank"] !== "") {
        res["target_rank"] = parseInt(formInfo["tarRank"]);
    } else {
        res["target_rank"] = maxRank;
    }
    var curEquip = "";
    var tarEquip = "";
    for (var i = 1; i <= 6; i++) {
        if (formInfo.hasOwnProperty("cur" + i)) {
            curEquip += "1";
        } else {
            curEquip += "0";
        }
        if (formInfo.hasOwnProperty("tar" + i)) {
            tarEquip += "1";
        } else {
            tarEquip += "0";
        }
    }
    res["cur_equip"] = curEquip;
    res["target_equip"] = tarEquip;
    return res;
}

/**
 * 比较函数，用于将所需的材料排序
 * @param obj1
 * @param obj2
 * @returns {number}
 */
function sortCraft(obj1, obj2) {
    return obj1.slice(2, 6) - obj2.slice(2, 6);
}

function getNeedCraft() {
    var craftBoxes = document.getElementsByClassName("craftBox");
    var needCraft = {};
    needCraft.crafts = {};
    for (var box of craftBoxes) {
        var curBox = $(box);
        //console.log(curBox);
        var craftId = curBox[0].childNodes[0].attributes["unit_id"].nodeValue;
        //console.log(craftId);
        var needNum = parseInt(curBox[0].childNodes[1].childNodes[0].data);
        //console.log(craftNum);
        var hasNum = parseInt(curBox[0].childNodes[2].value);
        //console.log(needNum);
        needCraft.crafts[craftId] = needNum - hasNum;
    }
    needCraft.maxMap = "";
    $.ajax({
        url: "/cal/scheme",
        type: "POST",
        data: JSON.stringify(needCraft),
        dataType: "json",
        success: function (data) {
            //console.log(data.scheme);
            var needAreas = "";
            var schemeContainer = document.getElementById("schemeContainer");
            if (data.status === 'success') {
                var areaPerLine = 3;
                var scheme = data.scheme;
                var counter = 1;
                for (var area of scheme) {
                    needAreas = needAreas + area[0] + ", " + area[1] + "&nbsp&nbsp";
                    if (counter % areaPerLine === 0) {
                        needAreas += "<br>";
                    }
                    counter++;
                }
                schemeContainer.innerHTML = needAreas;
            }
            //document.getElementById("schemeContainer").innerHTML = data.scheme;
        }
    });
    console.log(needCraft);
}

function drawUnitList(charaList, unitList) {
    removeAllChild("unitList");
    for (var unit of Object.getOwnPropertyNames(charaList)) {
        //console.log(unit);
        unitList.appendChild(createUnit(unit, charaList[unit], "unit", false, {
            unitDiv: "col-sm-3",
            unitBox: "unitBox",
            img: "iconImg",
            text: "label label-default"
        }));
    }
}