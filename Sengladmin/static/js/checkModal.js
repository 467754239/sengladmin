function fillTree(data){
    var setting = {
        view: {
            selectedMulti: false
        },
        check: {
            enable: true
        },
        data: {
            simpleData: {
                enable: true
            }
        },
        callback: {
            onCheck: onCheck
        }
    };

    var zNodes=data

    var clearFlag = false;

    function onCheck(e, treeId, treeNode) {
        count();
        if (clearFlag) {
            clearCheckedOldNodes();
        }

        var zTree = $.fn.zTree.getZTreeObj("treeDemo");
        var checkNum = zTree.getCheckedNodes(true);
        var checkLen = zTree.getCheckedNodes(true).length;
        tree_datas=[];
        for(var i=0;i<checkLen;i++){
            tree_datas.push(checkNum[i].name)
        }

    }
    function clearCheckedOldNodes() {
        var zTree = $.fn.zTree.getZTreeObj("treeDemo"),
            nodes = zTree.getChangeCheckedNodes();
        for (var i=0, l=nodes.length; i<l; i++) {
            nodes[i].checkedOld = nodes[i].checked;
        }
    }

    function count() {
        var zTree = $.fn.zTree.getZTreeObj("treeDemo"),
            checkCount = zTree.getCheckedNodes(true).length,
            nocheckCount = zTree.getCheckedNodes(false).length,
            changeCount = zTree.getChangeCheckedNodes().length;
        var zTree = $.fn.zTree.getZTreeObj("treeDemo");
        var checkNum = zTree.getCheckedNodes(true);
        var checkLen = zTree.getCheckedNodes(true).length;
        tree_datas=[];
        for(var i=0;i<checkLen;i++){
            tree_datas.push(checkNum[i].name)
        }
    }

    function createTree() {
        $.fn.zTree.init($("#treeDemo"), setting, zNodes);
        count();
    }


    $(document).ready(function(){
        createTree();
    })
}
