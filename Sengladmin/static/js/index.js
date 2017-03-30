$(function(){
    $('.get_code').on(
        'click', function(){
            var register_account=$('#register_account').val();
            $.ajax({
                url:'/sengladmin/user/captcha/',
                type:'get',
                data:{'register_account':register_account},
                dataType:'json',
                success:function(resp){
                    if(resp.rsp_head.rsp_code!=200){
                        alert(resp.rsp_head.rsp_info)
                    }else{
                        alert('验证码已发送至邮箱')
                    }
                }
            })
        }
    );

    $('#logout').on(
        'click', function(){
            $.ajax({
                url: '/sengladmin/user/logout/',
                type: 'post',
                data: {},
                success: function(resp){
                    window.location.href="/sengladmin/"
                }
            })
        }
    );

    $('#button_submit').on(
        'click', function(){
            var account = $('#current_account').html();
            var old_pass = $('#old_password').val();
            var new_pass = $('#new_password').val();
            $.ajax({
                url: '/sengladmin/user/password/',
                type: 'post',
                data: {'original_password': old_pass, 'new_password': new_pass, 'account': account},
                success: function(resp){
                    alert(resp.rsp_head.rsp_info)
                }
            })
        }
    );

    $('.btnResetPass').on('click',function(){
        $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
    });

    $('#button_reset_pass').on(
        'click', function(){
            var account = $('[data-value=1]').parents('tr').find('td:first-child').text();
            $.ajax({
                url: '/sengladmin/user/password/',
                type: 'delete',
                data: {'account': account},
                success: function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/user/'
                },
                error: function(){
                    $('.resetPass').on(
                        'hide.bs.modal', function(){
                            $(this).removeData()
                        }
                    )
                }
            })
        }
    );

    $('.button_allot_role').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var user_account = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var user_name = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            $.ajax(
                {
                    url: '/sengladmin/user/',
                    type: 'get',
                    data: {'account': user_account},
                    success: function(resp){
                        $('#user_role').empty()
                        $('#user_role').append('<option></option>')
                        if(resp.rsp_head.rsp_code == 200){
                            $('#user_account').val(user_account)
                            $('#user_name').val(user_name)
                            roles = resp.rsp_body.roles
                            user_role = resp.rsp_body.user.role
                            $.each(
                                roles,
                                function(i, d){
                                    if(user_role == roles[i].name){
                                        var option = '<option selected>' + roles[i].name + '</option>'
                                    }else{
                                        var option = '<option>' + roles[i].name + '</option>'
                                    }
                                    $('#user_role').append(option)
                                }
                            )
                        }
                    }
                }
            )
        }
    );

    $('#button_set_role').on(
        'click', function(){
            var user_account = $('#user_account').val()
            var user_role = $('#user_role').val()
            $.ajax({
                url: '/sengladmin/user/',
                type: 'post',
                data: {'user_account': user_account, 'user_role': user_role},
                success: function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/user/'
                },
                error: function(){
                    $('.resetPass').on(
                        'hide.bs.modal', function(){
                            $(this).removeData()
                        }
                    )
                }
            })
        }
    );


    $('.btnGetRole').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var role_name = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            $.ajax(
                {   
                    url: '/sengladmin/role/',
                    type: 'get',
                    data: {'role_name': role_name},
                    success: function(resp){
                        if(resp.rsp_head.rsp_code == 200){
                            $('#show_role_name').val(resp.rsp_body.role.name)
                            $('#show_role_level').val(resp.rsp_body.role.level)
                            $('#show_role_desc').val(resp.rsp_body.role.description)
                            $('#show_role_users').val(resp.rsp_body.role.users)
                            $('#show_role_permissions').val(resp.rsp_body.role.permissions)
                        }
                    }
                }
            )
        }
    );

    $('.btnAllotPermission').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var role_name = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            $.ajax(
                {
                    url: '/sengladmin/role/permission/',
                    type: 'get',
                    data: {'role_name': role_name},
                    success: function(resp){
                        fillTree(resp.rsp_body.permissions)
                    }
                }
            )
        }
    );

    $('#button_allot_permission').on(
        'click', function(){
            var role_name = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var permission = tree_datas
            $.ajax(
                {
                    url: '/sengladmin/role/permission/',
                    type: 'post',
                    traditional: true,
                    data: {'role_name': role_name, 'permission': permission},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/role/'
                    },
                    error: function(){
                        $('.allotPermission').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );



    $('#add_permission').on(
        'click', function(){
            $.ajax({
                url: '/sengladmin/resource/',
                type: 'get',
                dataType: 'json',
                data: {},
                success:function(resp){
                    if(resp.rsp_head.rsp_code == 200){
                        var root_permissions = resp.rsp_body.permissions
                        $('#permission_superior').empty()
                        $('#permission_superior').append('<option>ROOT</option>')
                        $.each(
                            root_permissions,
                            function(i, d){
                                var option = '<option>' + root_permissions[i].name + '</option>'
                                $('#permission_superior').append(option)
                            }
                        )
                    }
                }
           })
        }
    );

    $('#button_add_permission').on(
        'click', function(){
            var data = {
                'name': $('#permission_name').val(),
                'desc': $('#permission_desc').val(),
                'url': $('#permission_url').val(),
                'superior': $('#permission_superior').val()
            }
            $.ajax({
                url: '/sengladmin/permission/',
                type: 'put',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/permission/'
                }
           })
        }
    );

    $('.btnModifyPermission').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var permission_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/permission/',
                    type: 'get',
                    data: {'permission_name': permission_name},
                    success: function(resp){
                        if(resp.rsp_head.rsp_code == 200){
                            $('#md_permission_name').val(resp.rsp_body.permission.name)
                            $('#md_permission_desc').val(resp.rsp_body.permission.description)
                            $('#md_permission_url').val(resp.rsp_body.permission.url)
                            $('#md_permission_superior').empty()
                            $('#md_permission_superior').append('<option>ROOT</option>')
                            var root_permissions = resp.rsp_body.permission.root_permissions
                            $.each(
                                root_permissions,
                                function(i, d){
                                    var option = '<option>' + root_permissions[i] + '</option>'
                                    $('#md_permission_superior').append(option)
                                }
                            )
                            $('#md_permission_superior').val(resp.rsp_body.permission.superior)
                        }
                    }
                }
            )
        }
    );

    $('#button_modify_permission').on(
        'click', function(){
            var data = {
                'name': $('#md_permission_name').val(),
                'desc': $('#md_permission_desc').val(),
                'url': $('#md_permission_url').val(),
                'superior': $('#md_permission_superior').val()
            }
            $.ajax({
                url: '/sengladmin/permission/',
                type: 'post',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/permission/'
                }
           })
        }
    );

    $(".btnRemovePermission").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );
    
            
    $('#button_remove_permission').on(
        'click', function(){
            var permission_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/permission/',
                    type: 'delete',
                    data: {'permission_name': permission_name},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/permission/'
                    }
                }
            )
        }
    );

    $('#add_consignee').on(
        'click', function(){
            $.ajax({
                url: '/sengladmin/resource/',
                type: 'get',
                dataType: 'json',
                data: {},
                success:function(resp){
                    if(resp.rsp_head.rsp_code == 200){
                        var services = resp.rsp_body.services
                        $('#consignee_service').empty()
                        $('#consignee_service').append('<option>NULL</option>')
                        $.each(
                            services,
                            function(i, d){
                                var option = '<option>' + services[i].name + '</option>'
                                $('#consignee_service').append(option)
                            }
                        )
                    }
                }
           })
        }
    );

    $('#button_add_consignee').on(
        'click', function(){
            var data = {
                'name': $('#consignee_name').val(),
                'email': $('#consignee_email').val(),
                'group': $('#consignee_group').val(),
                'service': $('#consignee_service').val()
            }
            console.log(data)
            $.ajax({
                url: '/sengladmin/consignee/',
                type: 'put',
                dataType: 'json',
                data: data,
                traditional: true,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/consignee/'
                }
           })
        }
    );

    $('.btnModifyConsignee').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var consignee_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/consignee/',
                    type: 'get',
                    data: {'consignee_name': consignee_name},
                    success: function(resp){
                        $('#md_consignee_service').empty()
                        if(resp.rsp_head.rsp_code == 200){
                            $('#md_consignee_name').val(resp.rsp_body.consignee.name)
                            $('#md_consignee_email').val(resp.rsp_body.consignee.email)
                            $('#md_consignee_group').val(resp.rsp_body.consignee.group)
                            var services = resp.rsp_body.service
                            $.each(
                                services,
                                function(i, d){
                                    if(0 > jQuery.inArray(services[i].name, resp.rsp_body.consignee.service)){
                                        var option = '<li>' + services[i].name + '</li>'
                                    }else{
                                        var option = '<li class="height">' + services[i].name + '</li>'
                                    }
                                    $('#md_consignee_service').append(option)
                                }
                            )
                        }
                    }
                }
            )
        }
    );

    $('#button_modify_consignee').on(
        'click', function(){
            var select_service = $('#md_consignee_service>li.height')
            var services = []
            for(var i=0;i<select_service.length;i++){
                services.push(select_service.eq(i).html())
            }
            var data = {
                'name': $('#md_consignee_name').val(),
                'email': $('#md_consignee_email').val(),
                'group': $('#md_consignee_group').val(),
                'service': services
            }
            $.ajax({
                url: '/sengladmin/consignee/',
                type: 'post',
                dataType: 'json',
                data: data,
                traditional: true,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/consignee/'
                }
           })
        }
    );

    $(".btnRemoveConsignee").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_remove_consignee').on(
        'click', function(){
            var consignee_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/consignee/',
                    type: 'delete',
                    data: {'consignee_name': consignee_name},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/consignee/'
                    },
                    error: function(){
                        $('.removeConsignee').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $('#button_add_datacenter').on(
        'click', function(){
            var data = {
                'name': $('#dc_name').val(),
                'location': $('#dc_location').val(),
                'env': $('#dc_env').val(),
                'type': $('#dc_type').val(),
                'region': $('#dc_region').val(),
                'deploy_region': $('#dc_deploy_region').val(),
                'deploy_bucket': $('#dc_deploy_bucket').val(),
                'qurom_domain': $('#dc_qurom_domain').val(),
                'qurom_port': $('#dc_qurom_port').val(),
                'qurom_cacert': $('#dc_qurom_cacert').val(),
                'qurom_cakey': $('#dc_qurom_cakey').val(),
                'agent_version': $('#dc_agent_version').val(),
                'agent_file_path': $('#dc_agent_file_path').val(),
                'agent_access_key': $('#dc_agent_access_key').val(),
                'agent_secret_access': $('#dc_agent_secret_access').val()
            }
            $.ajax({
                url: '/sengladmin/datacenter/',
                type: 'put',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/datacenter/'
                }
           })
        }
    );

    $('#button_modify_datacenter').on(
        'click', function(){
            var data = {
                'name': $('#md_dc_name').val(),
                'location': $('#md_dc_location').val(),
                'env': $('#md_dc_env').val(),
                'type': $('#md_dc_type').val(),
                'region': $('#md_dc_region').val(),
                'deploy_region': $('#md_dc_deploy_region').val(),
                'deploy_bucket': $('#md_dc_deploy_bucket').val(),
                'qurom_domain': $('#md_dc_qurom_domain').val(),
                'qurom_port': $('#md_dc_qurom_port').val(),
                'qurom_cacert': $('#md_dc_qurom_cacert').val(),
                'qurom_cakey': $('#md_dc_qurom_cakey').val(),
                'agent_version': $('#md_dc_agent_version').val(),
                'agent_file_path': $('#md_dc_agent_file_path').val(),
                'agent_access_key': $('#md_dc_agent_access_key').val(),
                'agent_secret_access': $('#md_dc_agent_secret_access').val()
            }
            $.ajax({ 
                url: '/sengladmin/datacenter/',
                type: 'post',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/datacenter/'
                }
           })
        }
    );

    $('.btnGetDatacenter,.btnModifyDatacenter').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var datacenter_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/datacenter/',
                    type: 'get',
                    data: {'datacenter_name': datacenter_name},
                    success: function(resp){
                        if(resp.rsp_head.rsp_code == 200){
                            $('#show_dc_name').val(resp.rsp_body.datacenter.name)
                            $('#show_dc_type').val(resp.rsp_body.datacenter.type)
                            $('#show_dc_env').val(resp.rsp_body.datacenter.env)
                            $('#show_dc_location').val(resp.rsp_body.datacenter.location)
                            $('#show_dc_region').val(resp.rsp_body.datacenter.region)
                            $('#show_dc_agent_version').val(resp.rsp_body.datacenter.agent.version)
                            $('#show_dc_agent_file_path').val(resp.rsp_body.datacenter.agent.file_path)
                            $('#show_dc_agent_access_key').val(resp.rsp_body.datacenter.agent.access_key_id)
                            $('#show_dc_agent_secret_access').val(resp.rsp_body.datacenter.agent.secret_access_key)
                            $('#show_dc_deploy_region').val(resp.rsp_body.datacenter.deploy.region)
                            $('#show_dc_deploy_bucket').val(resp.rsp_body.datacenter.deploy.bucket)
                            $('#show_dc_qurom_domain').val(resp.rsp_body.datacenter.qurom.domain)
                            $('#show_dc_qurom_port').val(resp.rsp_body.datacenter.qurom.port)
                            $('#show_dc_qurom_cacert').val(resp.rsp_body.datacenter.qurom.cacert)
                            $('#show_dc_qurom_cakey').val(resp.rsp_body.datacenter.qurom.cakey)

                            $('#md_dc_name').val(resp.rsp_body.datacenter.name)
                            $('#md_dc_type').val(resp.rsp_body.datacenter.type)
                            $('#md_dc_env').val(resp.rsp_body.datacenter.env)
                            $('#md_dc_location').val(resp.rsp_body.datacenter.location)
                            $('#md_dc_region').val(resp.rsp_body.datacenter.region)
                            $('#md_dc_agent_version').val(resp.rsp_body.datacenter.agent.version)
                            $('#md_dc_agent_file_path').val(resp.rsp_body.datacenter.agent.file_path)
                            $('#md_dc_agent_access_key').val(resp.rsp_body.datacenter.agent.access_key_id)
                            $('#md_dc_agent_secret_access').val(resp.rsp_body.datacenter.agent.secret_access_key)
                            $('#md_dc_deploy_region').val(resp.rsp_body.datacenter.deploy.region)
                            $('#md_dc_deploy_bucket').val(resp.rsp_body.datacenter.deploy.bucket)
                            $('#md_dc_qurom_domain').val(resp.rsp_body.datacenter.qurom.domain)
                            $('#md_dc_qurom_port').val(resp.rsp_body.datacenter.qurom.port)
                            $('#md_dc_qurom_cacert').val(resp.rsp_body.datacenter.qurom.cacert)
                            $('#md_dc_qurom_cakey').val(resp.rsp_body.datacenter.qurom.cakey)
                        }
                    }
                }
            )
        }
    );

    $(".btnLockDatacenter").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var env_type = $('[data-value=1]').parents('tr').find('td:nth-child(3)').text();
            if (env_type != 'test'){
                alert('该数据中心不是测试环境, 不需要锁定')
                $(this).attr('data-target', '') 
                return
            }
        }
    );

    $('#button_lock_datacenter').on(
        'click', function(){
            var datacenter_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/datacenter/status/',
                    type: 'post',
                    data: {'name': datacenter_name, 'status': 'lock'},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/datacenter/'
                    },
                    error: function(){
                        $('.lockDatacenter').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $(".btnUnlockDatacenter").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var env_type = $('[data-value=1]').parents('tr').find('td:nth-child(3)').text();
            if (env_type != 'test'){
                alert('该数据中心不是测试环境, 不需要解除锁定')
                $(this).attr('data-target', '') 
                return
            }
        }
    );

    $('#button_unlock_datacenter').on(
        'click', function(){
            var datacenter_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/datacenter/status/',
                    type: 'post',
                    data: {'name': datacenter_name, 'status': 'unlock'},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/datacenter/'
                    },
                    error: function(){
                        $('.unlockDatacenter').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $(".btnSyncDatacenter").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_sync_datacenter').on(
        'click', function(){
            var datacenter_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/consul/datacenter/',
                    type: 'post',
                    data: {'name': datacenter_name},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/datacenter/'
                    },
                    error: function(){
                        $('.syncDatacenter').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $(".btnRemoveDatacenter").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_remove_datacenter').on(
        'click', function(){
            var datacenter_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var authorize = $('#authorize').val()
            $.ajax(
                {
                    url: '/sengladmin/datacenter/',
                    type: 'delete',
                    data: {'datacenter_name': datacenter_name, 'authorize': authorize},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/datacenter/'
                    },
                    error: function(){
                        $('.removeDatacenter').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $('#button_add_service').on(
        'click', function(){
            var data = {
                'name': $('#service_name').val(),
                'description': $('#service_desc').val(),
                'git_path': $('#service_git_path').val(),
                /*'build_env_type': $('#service_build_env_type').val(),
                'build_env_value': $('#service_build_env_value').val(),*/
                'build_trigger': $('input:radio[name="gender"]:checked').val(),
                'build_trigger_str': $('#service_build_trigger_str').val(),
                'build_docker_image_id': $('#service_build_docker_image_id').val(),
            }
            $.ajax({
                url: '/sengladmin/develop/service/',
                type: 'put',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/develop/service/'
                }   
           })   
        }  
    );

    $(".btnLockService").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_lock_service').on(
        'click', function(){
            var service_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/service/status/',
                    type: 'post',
                    data: {'name': service_name, 'status': 'lock'},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/service/'
                    },
                    error: function(){
                        $('.lockService').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $(".btnUnlockService").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_unlock_service').on(
        'click', function(){
            var service_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/service/status/',
                    type: 'post',
                    data: {'name': service_name, 'status': 'unlock'},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/service/'
                    },
                    error: function(){
                        $('.unlockService').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $(".btnRemoveService").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_remove_service').on(
        'click', function(){
            var service_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/service/',
                    type: 'delete',
                    data: {'name': service_name},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/develop/service/'
                    },
                    error: function(){
                        $('.removeService').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $('.btnGetService, .btnModifyService').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var service_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/develop/service/',
                    type: 'get',
                    data: {'service_name': service_name},
                    success: function(resp){
                        if(resp.rsp_head.rsp_code == 200){
                            $('#show_service_name').val(resp.rsp_body.service.name)
                            $('#show_service_desc').val(resp.rsp_body.service.description)
                            $('#show_service_git_path').val(resp.rsp_body.service.git_path)
                            /*if(resp.rsp_body.service.build_env.build_env_type != null) {
                                $('#show_service_build_env_type').append('<option selected>' + resp.rsp_body.service.build_env.build_env_type + '</option>')
                            }
                            else {
                                $('#show_service_build_env_type').val('NULL')
                            }
                            if(resp.rsp_body.service.build_env.build_env_value != null) {
                                $('#show_service_build_env_value').append('<option selected>' + resp.rsp_body.service.build_env.build_env_value + '</option>')
                            }
                            else {
                                $('#show_service_build_env_value').val('NULL')
                            }
                            */
                            if(resp.rsp_body.service.build_trigger == 'manual') {
                                $('#genderShowManual').iCheck('check')
                            }
                            else if (resp.rsp_body.service.build_trigger != null) {
                                $('#genderShowAuto').iCheck('check')
                                $('#show_service_build_trigger_str').val(resp.rsp_body.service.build_trigger)
                            }
                            else {
                                $('#genderShowManual').iCheck('uncheck')
                                $('#genderShowAuto').iCheck('uncheck')
                                $('#show_service_build_trigger_str').val("")
                            }
                            $('#genderShowManual').attr('disabled','disabled')
                            $('#genderShowAuto').attr('disabled','disabled')
                            $('#show_service_status').val(resp.rsp_body.service.status)
                            $('#show_service_datacenters').val(resp.rsp_body.service.datacenters)
                            $('#show_service_build_docker_image_id').val(resp.rsp_body.service.build_docker_image)

                            $('#modify_service_name').val(resp.rsp_body.service.name)
                            $('#modify_service_desc').val(resp.rsp_body.service.description)
                            $('#modify_service_git_path').val(resp.rsp_body.service.git_path)
                            /*if(resp.rsp_body.service.build_env.build_env_type != null) {
                                $('#modify_service_build_env_type').val(resp.rsp_body.service.build_env.build_env_type)
                            }
                            else {
                                $('#modify_service_build_env_type').val('NULL')
                            }
                            if(resp.rsp_body.service.build_env.build_env_value != null) {
                                $('#modify_service_build_env_value').val(resp.rsp_body.service.build_env.build_env_value)
                            }
                            else {
                                $('#modify_service_build_env_value').val('NULL')
                            }
                            */
                            if(resp.rsp_body.service.build_trigger == 'manual') {
                                $('#genderModifyManual').iCheck('check')
                            }
                            else if (resp.rsp_body.service.build_trigger != null) {
                                $('#genderModifyAuto').iCheck('check')
                                $('#modify_service_build_trigger_str').val(resp.rsp_body.service.build_trigger)
                            }
                            else{
                                $('#genderModifyManual').iCheck('uncheck')
                                $('#genderModifyAuto').iCheck('uncheck')
                                $('#modify_service_build_trigger_str').val("")
                            }
                            $('#modify_service_status').val(resp.rsp_body.service.status)
                            $('#modify_service_datacenters').val(resp.rsp_body.service.datacenters)
                            $('#modify_service_build_docker_image_id').val(resp.rsp_body.service.build_docker_image)
                        }
                    }
                }
            )
        }
    );

    $('#button_modify_service').on(
        'click', function(){
            var data = {
                'name': $('#modify_service_name').val(),
                'description': $('#modify_service_desc').val(),
                'git_path': $('#modify_service_git_path').val(),
                'build_env_type': $('#modify_service_build_env_type').val(),
                'build_env_value': $('#modify_service_build_env_value').val(),
                'build_trigger': $('input:radio[name="genderModify"]:checked').val(),
                //'build_trigger_str': $('#modify_service_build_trigger_str').val(),
                'build_trigger_str': '* * * * *',
                'build_docker_image_id': $('#modify_service_build_docker_image_id').val()
            }
            $.ajax({
                url: '/sengladmin/develop/service/',
                type: 'post',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/develop/service/'
                }
           })
        }
    );

    $('#add_group').on(
        'click', function(){
            $.ajax({
                url: '/sengladmin/resource/',
                type: 'get',
                dataType: 'json',
                data: {},
                success:function(resp){
                    if(resp.rsp_head.rsp_code == 200){
                        var datacenters = resp.rsp_body.datacenters
                        var services = resp.rsp_body.services
                        $('#group_datacenter').empty()
                        $('#group_service').empty()
                        $.each(
                            datacenters,
                            function(i, d){
                                var option = '<option>' + datacenters[i].name + '</option>'
                                $('#group_datacenter').append(option)
                            }
                        )
                        $.each(
                            services,
                            function(i, d){
                                var option = '<option>' + services[i].name + '</option>'
                                $('#group_service').append(option)
                            }
                        )
                    }
                }
           })
        }
    );

    $('#button_add_group').on(
        'click', function(){
            var data = {
                'name': $('#group_name').val(),
                'service': $('#group_service').val(),
                'version': $('#group_version').val(),
                'datacenter': $('#group_datacenter').val(),
                'rm_type': $('#group_rm_type').val(),
                'rm_name': $('#group_rm_name').val(),
                'deploy_type': $('#group_deploy_type').val(),
                'deploy_value': $('#group_deploy_value').val()
            }
            $.ajax({
                url: '/sengladmin/group/',
                type: 'put',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/group/'
                }
           })
        }
    );

    $('.btnGetGroup, .btnModifyGroup').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var group_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax( 
                {   
                    url: '/sengladmin/group/',
                    type: 'get',
                    data: {'group_name': group_name},
                    success: function(resp){
                        $('#show_group_service').empty()
                        $('#show_group_datacenter').empty()
                        $('#md_group_service').empty()
                        $('#md_group_datacenter').empty()
                        if(resp.rsp_head.rsp_code == 200){
                            $('#show_group_name').val(resp.rsp_body.group.name)
                            $('#show_group_service').append('<option>' + resp.rsp_body.group.service + '</option>')
                            $('#show_group_service').val(resp.rsp_body.group.service)
                            $('#show_group_version').val(resp.rsp_body.group.version)
                            $('#show_group_datacenter').append('<option>' + resp.rsp_body.group.datacenter + '</option>')
                            $('#show_group_datacenter').val(resp.rsp_body.group.datacenter)
                            $('#show_group_rm_type').val(resp.rsp_body.group.group.type)
                            $('#show_group_rm_name').val(resp.rsp_body.group.group.name)
                            $('#show_group_deploy_type').val(resp.rsp_body.group.deploy.type)
                            $('#show_group_deploy_value').val(resp.rsp_body.group.deploy.value)
                            $('#show_group_healthchecks').val(resp.rsp_body.group.healthchecks)
                            $('#show_group_monitors').val(resp.rsp_body.group.monitors)

                            $('#md_group_name').val(resp.rsp_body.group.name)
                            $('#md_group_service').append('<option>' + resp.rsp_body.group.service + '</option>')
                            $('#md_group_service').val(resp.rsp_body.group.service)
                            $('#md_group_version').val(resp.rsp_body.group.version)
                            $('#md_group_datacenter').append('<option>' + resp.rsp_body.group.datacenter + '</option>')
                            $('#md_group_datacenter').val(resp.rsp_body.group.datacenter)
                            $('#md_group_rm_type').val(resp.rsp_body.group.group.type)
                            $('#md_group_rm_name').val(resp.rsp_body.group.group.name)
                            $('#md_group_deploy_type').val(resp.rsp_body.group.deploy.type)
                            $('#md_group_deploy_value').val(resp.rsp_body.group.deploy.value)
                            $('#md_group_healthchecks').val(resp.rsp_body.group.healthchecks)
                            $('#md_group_monitors').val(resp.rsp_body.group.monitors)
                        }
                    }
                }
            )
        }
    );

    $('#button_modify_group').on(
        'click', function(){
            var data = {
                'name': $('#md_group_name').val(),
                'rm_type': $('#md_group_rm_type').val(),
                'rm_name': $('#md_group_rm_name').val(),
                'deploy_type': $('#md_group_deploy_type').val(),
                'deploy_value': $('#md_group_deploy_value').val()
            }
            $.ajax({
                url: '/sengladmin/group/',
                type: 'post',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/group/'
                }
           })
        }
    );

    $(".btnSyncConfig").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_sync_config').on(
        'click', function(){
            var group_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/consul/config/',
                    type: 'post',
                    data: {'name': group_name},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/group/'
                    },
                    error: function(){
                        $('.syncConfig').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $(".btnRemoveGroup").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_remove_group').on(
        'click', function(){
            var group_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var authorize = $('#authorize').val()
            $.ajax(
                {
                    url: '/sengladmin/group/',
                    type: 'delete',
                    data: {'name': group_name, 'authorize': authorize},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/group/'
                    },
                    error: function(){
                        $('.removeGroup').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $('#add_config').on(
        'click', function(){
            $.ajax({
                url: '/sengladmin/resource/',
                type: 'get',
                dataType: 'json',
                data: {},
                success:function(resp){
                    if(resp.rsp_head.rsp_code == 200){
                        var datacenters = resp.rsp_body.datacenters
                        var services = resp.rsp_body.services
                        $('#config_datacenter').empty()
                        $('#config_domain').empty()
                        $.each(
                            datacenters,
                            function(i, d){
                                var option = '<option>' + datacenters[i].name + '</option>'
                                $('#config_datacenter').append(option)
                            }
                        )

                        $('#config_domain').append(
                            '<optgroup label="全局" class="optgroup-custom">' + 
                            '<option>GLOBAL</option>' +
                            '</optgroup>'
                        )
                        var domain_option = '<optgroup label="服务" class="optgroup-custom">'
                        $.each(
                            services,
                            function(i, d){
                                domain_option += '<option>' + services[i].name + '</option>'
                            }
                        )
                        domain_option += '</optgroup>'
                        $('#config_domain').append(domain_option)
                    }
                }
           })
        }
    );

    $('#button_add_config').on(
        'click', function(){
            var data = {
                'key': $('#config_key').val(),
                'description': $('#description').val(),
                'value': $('#config_value').val(),
                'consul_key': $('#config_consul_key').val(),
                'consul_value': $('#config_consul_value').val(),
                'datacenter': $('#config_datacenter').val(),
                'domain': $('#config_domain').val()
            }
            $.ajax({ 
                url: '/sengladmin/config/',
                type: 'put',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/config/'
                }
           })
        }
    );

    $('.btnGetConfig, .btnModifyConfig').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var config_key = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var config_datacenter = $('[data-value=1]').parents('tr').find('td:nth-child(4)').text();
            var config_domain = $('[data-value=1]').parents('tr').find('td:nth-child(5)').text();
            $.ajax(
                {   
                    url: '/sengladmin/config/',
                    type: 'get',
                    data: {'key': config_key, 'datacenter': config_datacenter, 'domain': config_domain},
                    success: function(resp){
                        $('#show_config_datacenter').empty()
                        $('#show_config_domain').empty()
                        $('#md_config_datacenter').empty()
                        $('#md_config_domain').empty()
                        if(resp.rsp_head.rsp_code == 200){
                            $('#show_config_key').val(resp.rsp_body.config.key)
                            $('#show_config_description').val(resp.rsp_body.config.description)
                            $('#show_config_value').val(resp.rsp_body.config.value)
                            $('#show_config_consul_key').val(resp.rsp_body.config.consul_key)
                            $('#show_config_consul_value').val(resp.rsp_body.config.consul_value)
                            $('#show_config_datacenter').append('<option>' + resp.rsp_body.config.datacenter + '</option>')
                            $('#show_config_domain').append('<option>' + resp.rsp_body.config.domain + '</option>')

                            $('#md_config_key').val(resp.rsp_body.config.key)
                            $('#md_config_description').val(resp.rsp_body.config.description)
                            $('#md_config_value').val(resp.rsp_body.config.value)
                            $('#md_config_consul_key').val(resp.rsp_body.config.consul_key)
                            $('#md_config_consul_value').val(resp.rsp_body.config.consul_value)
                            $('#md_config_datacenter').append('<option>' + resp.rsp_body.config.datacenter + '</option>')
                            $('#md_config_domain').append('<option>' + resp.rsp_body.config.domain + '</option>')
                        }
                    }
                }
            )
        }
    );

    $('#button_modify_config').on(
        'click', function(){
            var data = {
                'key': $('#md_config_key').val(),
                'description': $('#md_config_description').val(),
                'value': $('#md_config_value').val(),
                'consul_value': $('#md_config_consul_value').val(),
                'datacenter': $('#md_config_datacenter').val(),
                'domain': $('#md_config_domain').val()
            }
            $.ajax({
                url: '/sengladmin/config/',
                type: 'post',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/config/'
                }
           })
        }
    );

    $(".btnRemoveConfig").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_remove_config').on(
        'click', function(){
            var config_key = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var config_datacenter = $('[data-value=1]').parents('tr').find('td:nth-child(4)').text();
            var config_domain = $('[data-value=1]').parents('tr').find('td:nth-child(5)').text();
            $.ajax(
                {
                    url: '/sengladmin/config/',
                    type: 'delete',
                    data: {'key': config_key, 'datacenter': config_datacenter, 'domain': config_domain},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/config/'
                    },
                    error: function(){
                        $('.removeConfig').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $('#button_add_health').on(
        'click', function(){
            var data = {
                'name': $('#health_name').val(),
                'type': $('#health_type').val(),
                'value': $('#health_value').val(),
                'interval': $('#health_interval').val(),
                'timeout': $('#health_timeout').val(),
                'pending': $('#health_pending').val(),
                'healthy_threshold': $('#health_healthy_threshold').val(),
                'unhealthy_threshold': $('#health_unhealthy_threshold').val(),
                'failback': $('#health_failback').val()
            }
            $.ajax({
                url: '/sengladmin/health/',
                type: 'put',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/health/'
                }
           })
        }
    );

    $('.btnGetHealth, .btnModifyHealth').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var health_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/health/',
                    type: 'get',
                    data: {'health_name': health_name},
                    success: function(resp){
                        if(resp.rsp_head.rsp_code == 200){
                            $('#show_health_name').val(resp.rsp_body.health.name)
                            $('#show_health_type').val(resp.rsp_body.health.type)
                            $('#show_health_value').val(resp.rsp_body.health.value)
                            $('#show_health_interval').val(resp.rsp_body.health.interval)
                            $('#show_health_timeout').val(resp.rsp_body.health.timeout)
                            $('#show_health_pending').val(resp.rsp_body.health.pending)
                            $('#show_health_healthy_threshold').val(resp.rsp_body.health.healthy_threshold)
                            $('#show_health_unhealthy_threshold').val(resp.rsp_body.health.unhealthy_threshold)
                            $('#show_health_failback').val(resp.rsp_body.health.failback)
                            $('#show_health_associate').val(resp.rsp_body.health.associate)

                            $('#md_health_name').val(resp.rsp_body.health.name)
                            $('#md_health_type').val(resp.rsp_body.health.type)
                            $('#md_health_value').val(resp.rsp_body.health.value)
                            $('#md_health_interval').val(resp.rsp_body.health.interval)
                            $('#md_health_timeout').val(resp.rsp_body.health.timeout)
                            $('#md_health_pending').val(resp.rsp_body.health.pending)
                            $('#md_health_healthy_threshold').val(resp.rsp_body.health.healthy_threshold)
                            $('#md_health_unhealthy_threshold').val(resp.rsp_body.health.unhealthy_threshold)
                            $('#md_health_failback').val(resp.rsp_body.health.failback)
                            $('#md_health_associate').val(resp.rsp_body.health.associate)
                        }
                    }
                }
            )
        }   
    );
    
    $('#button_modify_health').on(
        'click', function(){
            var data = {
                'name': $('#md_health_name').val(),
                'type': $('#md_health_type').val(),
                'value': $('#md_health_value').val(),
                'interval': $('#md_health_interval').val(),
                'timeout': $('#md_health_timeout').val(),
                'pending': $('#md_health_pending').val(),
                'healthy_threshold': $('#md_health_healthy_threshold').val(),
                'unhealthy_threshold': $('#md_health_unhealthy_threshold').val(),
                'failback': $('#md_health_failback').val()
            }
            $.ajax({
                url: '/sengladmin/health/',
                type: 'post',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/health/'
                }
           })
        }
    );

    $(".btnRemoveHealth").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_remove_health').on(
        'click', function(){
            var health_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/health/',
                    type: 'delete',
                    data: {'name': health_name},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/health/'
                    },
                    error: function(){
                        $('.removeHealth').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $('#button_add_monitor').on(
        'click', function(){
            var data = {
                'name': $('#monitor_name').val(),
                'type': $('#monitor_type').val(),
                'value': $('#monitor_value').val()
            }
            $.ajax({
                url: '/sengladmin/monitor/',
                type: 'put',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/monitor/'
                }
           })
        }
    );

    $('.btnGetMonitor, .btnModifyMonitor').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var monitor_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/monitor/',
                    type: 'get',
                    data: {'monitor_name': monitor_name},
                    success: function(resp){
                        if(resp.rsp_head.rsp_code == 200){
                            $('#show_monitor_name').val(resp.rsp_body.monitor.name)
                            $('#show_monitor_type').val(resp.rsp_body.monitor.type)
                            $('#show_monitor_value').val(resp.rsp_body.monitor.value)
                            $('#show_monitor_associate').val(resp.rsp_body.monitor.associate)

                            $('#md_monitor_name').val(resp.rsp_body.monitor.name)
                            $('#md_monitor_type').val(resp.rsp_body.monitor.type)
                            $('#md_monitor_value').val(resp.rsp_body.monitor.value)
                            $('#md_monitor_associate').val(resp.rsp_body.monitor.associate)
                        }
                    }
                }
            )
        }
    );

    $('#button_modify_monitor').on(
        'click', function(){
            var data = {
                'name': $('#md_monitor_name').val(),
                'type': $('#md_monitor_type').val(),
                'value': $('#md_monitor_value').val()
            }
            $.ajax({
                url: '/sengladmin/monitor/',
                type: 'post',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/monitor/'
                }
           })
        }
    );

    $(".btnRemoveMonitor").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_remove_monitor').on(
        'click', function(){
            var monitor_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/monitor/',
                    type: 'delete',
                    data: {'name': monitor_name},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/monitor/'
                    },
                    error: function(){
                        $('.removeMonitor').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $('#add_package').on(
        'click', function(){
            $.ajax({
                url: '/sengladmin/resource/',
                type: 'get',
                dataType: 'json',
                data: {},
                success:function(resp){
                    if(resp.rsp_head.rsp_code == 200){
                        var services = resp.rsp_body.services
                        $('#package_service').empty()
                        $.each(
                            services,
                            function(i, d){
                                var option = '<option>' + services[i].name + '</option>'
                                $('#package_service').append(option)
                            }
                        )
                    }
                }
           })
        }
    );

    $('#button_add_package').on(
        'click', function(){
            var data = {
                'service': $('#package_service').val(),
                'version': $('#package_version').val(),
                'md5': $('#package_md5').val(),
                'region': $('#package_region').val(),
                'bucket': $('#package_bucket').val(),
                'file_path': $('#package_file_path').val()
            }
            $.ajax({
                url: '/sengladmin/package/',
                type: 'put',
                dataType: 'json',
                data: data,
                success:function(resp){
                    alert(resp.rsp_head.rsp_info)
                    window.location.href = '/sengladmin/package/'
                }
           })
        }
    );

    $(".btnRemovePackage").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_remove_package').on(
        'click', function(){
            var package_service = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var package_version = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var authorize = $('#authorize').val()
            $.ajax(
                {
                    url: '/sengladmin/package/',
                    type: 'delete',
                    data: {'authorize': authorize, 'service': package_service, 'version': package_version},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/package/'
                    },
                    error: function(){
                        $('.removePackage').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $('.btnGetPackage').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var package_service = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var package_version = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            $('#show_package_service').empty()
            $.ajax(
                {
                    url: '/sengladmin/package/',
                    type: 'get',
                    data: {'service': package_service, 'version': package_version},
                    success: function(resp){
                        if(resp.rsp_head.rsp_code == 200){
                            var option = '<option>' + resp.rsp_body.package.service + '</option>'
                            $('#show_package_service').append(option)
                            $('#show_package_version').val(resp.rsp_body.package.version)
                            $('#show_package_md5').val(JSON.stringify(resp.rsp_body.package.md5))
                            $('#show_package_region').val(resp.rsp_body.package.region)
                            $('#show_package_bucket').val(resp.rsp_body.package.bucket)
                            $('#show_package_file_path').val(resp.rsp_body.package.file_path)
                            $('#show_package_time').val(resp.rsp_body.package.time)
                            
                            $('#show_package_status_md5').val(resp.rsp_body.package.status.md5)
                            $('#show_package_status_sql').val(resp.rsp_body.package.status.sql)
                            $('#show_package_status_port').val(resp.rsp_body.package.status.port)
                            $('#show_package_status_config').val(resp.rsp_body.package.status.config)
                            $('#show_package_status_deploy').val(resp.rsp_body.package.status.deploy)
                        }
                    }
                }
            )
        }
    );

    $(".btnPassPort").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var package_service = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var package_version = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var status = $('[data-value=1]').parents('tr').find('td:nth-child(5)').text();
            if (status != 'waiting'){
                alert('该状态不需要进行审核')
                $(this).attr('data-target', '')
                return
            }
        }
    );
            
    $('#button_pass_port').on(
        'click', function(){
            var package_service = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var package_version = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var authorize = $('input[name="authorize_pass_port"]').val()
            $.ajax(
                {
                    url: '/sengladmin/audit/',
                    type: 'post',
                    data: {'authorize': authorize, 'service': package_service, 'version': package_version, 'type': 'port', 'status': 'pass'},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/audit/'
                    },
                    error: function(){
                        $('.passPort').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $(".btnRefusePort").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var package_service = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var package_version = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var status = $('[data-value=1]').parents('tr').find('td:nth-child(5)').text();
            if (status != 'waiting'){
                alert('该状态不需要进行审核')
                $(this).attr('data-target', '')
                return
            }
        }
    );

    $('#button_refuse_port').on(
        'click', function(){
            var package_service = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var package_version = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var authorize = $('input[name="authorize_refuse_port"]').val()
            $.ajax(
                {
                    url: '/sengladmin/audit/',
                    type: 'post',
                    data: {'authorize': authorize, 'service': package_service, 'version': package_version, 'type': 'port', 'status': 'refuse'},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/audit/'
                    },
                    error: function(){
                        $('.refusePort').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $(".btnPassConfig").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var package_service = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var package_version = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var status = $('[data-value=1]').parents('tr').find('td:nth-child(6)').text();
            if (status != 'waiting'){
                alert('该状态不需要进行审核')
                $(this).attr('data-target', '')
                return
            }
        }
    );

    $('#button_pass_config').on(
        'click', function(){
            var package_service = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var package_version = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var authorize = $('input[name="authorize_pass_config"]').val()
            $.ajax(
                {
                    url: '/sengladmin/audit/',
                    type: 'post',
                    data: {'authorize': authorize, 'service': package_service, 'version': package_version, 'type': 'config', 'status': 'pass'},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/audit/'
                    },
                    error: function(){
                        $('.passConfig').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $(".btnRefuseConfig").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var package_service = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var package_version = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var status = $('[data-value=1]').parents('tr').find('td:nth-child(6)').text();
            if (status != 'waiting'){
                alert('该状态不需要进行审核')
                $(this).attr('data-target', '')
                return
            }
        }
    );

    $('#button_refuse_config').on(
        'click', function(){
            var package_service = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var package_version = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var authorize = $('input[name="authorize_refuse_config"]').val()
            $.ajax(
                {
                    url: '/sengladmin/audit/',
                    type: 'post',
                    data: {'authorize': authorize, 'service': package_service, 'version': package_version, 'type': 'config', 'status': 'refuse'},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/audit/'
                    },
                    error: function(){
                        $('.refuseConfig').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $(".btnPassForce").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_pass_force').on(
        'click', function(){
            var package_service = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var package_version = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var authorize = $('input[name="authorize_pass_force"]').val()
            $.ajax(
                {
                    url: '/sengladmin/audit/force/',
                    type: 'post',
                    data: {'authorize': authorize, 'service': package_service, 'version': package_version},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/audit/'
                    },
                    error: function(){
                        $('.passForce').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $('.btnGetAudit').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var package_service = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var package_version = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            $('#show_package_service').empty()
            $.ajax(
                {
                    url: '/sengladmin/audit/',
                    type: 'get',
                    data: {'service': package_service, 'version': package_version},
                    success: function(resp){
                        if(resp.rsp_head.rsp_code == 200){
                            var option = '<option>' + resp.rsp_body.package.service + '</option>'
                            $('#show_package_service').append(option)
                            $('#show_package_version').val(resp.rsp_body.package.version)

                            $('#show_package_audit_port').val(resp.rsp_body.package.audit.port)
                            $('#show_package_audit_config').val(resp.rsp_body.package.audit.config)
                        }
                    }
                }
            )
        }
    );

    $('.btnLinkHealth').on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var group_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            
            $.ajax({
                url: '/sengladmin/resource/',
                type : 'get',
                dateType : 'json',
                data: {'group': group_name},
                success: function(resp){
                    if(resp.rsp_head.rsp_code == 200){
                        $('#exist_group_healthchecks').val(resp.rsp_body.group.healthchecks)

                        var healths = resp.rsp_body.healths;
                        var option='';
                        $.each(
                            healths,
                            function(i, d){
                                option += '<option>' + healths[i].name + '</option>'
                            }
                        )
                        $('#healthchecks').empty();
                        $('#healthchecks').append(option);
                        $('#healthchecks').bootstrapDualListbox('refresh', true)
                    }
                }
            })
        }
    );
            
    $('#button_link_health').on(
        'click', function(){
            var group_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var healths = '';
            $('#healthchecks option').each(function() {
                var attr = $(this).attr('data-sortindex')
                if (typeof attr !== typeof undefined && attr !== false) {
                    if (healths != ''){
                        healths += ',' + $(this).html()
                    }
                    else{
                        healths = $(this).html()
                    }
                }
            });

            $.ajax(
                {
                    url: '/sengladmin/consul/health/',
                    type: 'post',
                    data: {'group': group_name, 'healths': healths},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/group/'
                    },
                    error: function(){
                        $('.linkHealth').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $('.btnLinkMonitor').on(
        'click',function(){                                                                                     
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);        
            var group_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();                  
                    
            $.ajax({
                url: '/sengladmin/resource/',                                                                   
                type : 'get',
                dateType : 'json',
                data: {'group': group_name},
                success: function(resp){
                    if(resp.rsp_head.rsp_code == 200){
                        $('#exist_group_monitors').val(resp.rsp_body.group.monitors)                    
                            
                        var monitors = resp.rsp_body.monitors;                                                    
                        var option='';
                        $.each(
                            monitors,
                            function(i, d){                                                                     
                                option += '<option>' + monitors[i].name + '</option>'
                            }
                        )   
                        $("#monitors").empty();
                        $("#monitors").append(option);
                        $('#monitors').bootstrapDualListbox('refresh', true)
                    } 
                }
            })
        }
    );

    $('#button_link_monitor').on(
        'click', function(){
            var group_name = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();                  
            var monitors = '';
            $('#monitors option').each(function() {
                var attr = $(this).attr('data-sortindex')
                if (typeof attr !== typeof undefined && attr !== false) {
                    if (monitors != ''){
                        monitors += ',' + $(this).html()
                    }
                    else{
                        monitors = $(this).html()
                    }
                }
            });

            $.ajax(
                {
                    url: '/sengladmin/consul/monitor/',
                    type: 'post',
                    data: {'group': group_name, 'monitors': monitors},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/group/'
                    },
                    error: function(){
                        $('.linkMonitor').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $('.btnGetDeployRecord').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var deploy_id = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            $.ajax(
                {
                    url: '/sengladmin/deploy/record/',
                    type: 'get',
                    data: {'deploy_id': deploy_id},
                    success: function(resp){
                        if(resp.rsp_head.rsp_code == 200){
                            $('#show_deploy_record_id').val(resp.rsp_body.deploy_record.deploy_id)
                            $('#show_deploy_record_source_version').val(resp.rsp_body.deploy_record.source_version)
                            $('#show_deploy_record_target_version').val(resp.rsp_body.deploy_record.target_version)
                            $('#show_deploy_record_start_time').val(resp.rsp_body.deploy_record.start_time)
                            $('#show_deploy_record_end_time').val(resp.rsp_body.deploy_record.end_time)
                            $('#show_deploy_record_result').val(resp.rsp_body.deploy_record.result)
                            $('#show_deploy_record_env').val(resp.rsp_body.deploy_record.env)
                            $('#show_deploy_record_datacenter').val(resp.rsp_body.deploy_record.datacenter)
                            $('#show_deploy_record_group').val(resp.rsp_body.deploy_record.group)
                            $('#show_deploy_record_service').val(resp.rsp_body.deploy_record.service)
                            $('#show_deploy_record_operator').val(resp.rsp_body.deploy_record.operator)
                        }
                    }
                }
            )
        }
    );

    $(".btnSuccessDeployProcess").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_success_process').on(
        'click', function(){
            var deploy_id = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var instance = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            $.ajax(
                {
                    url: '/sengladmin/deploy/process/',
                    type: 'post',
                    data: {'deploy_id': deploy_id, 'instance': instance, 'status': 'success'},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/deploy/process/'
                    },
                    error: function(){
                        $('.successDeployProcess').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $(".btnFailDeployProcess").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
        }
    );

    $('#button_fail_process').on(
        'click', function(){
            var deploy_id = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var instance = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            $.ajax(
                {
                    url: '/sengladmin/deploy/process/',
                    type: 'post',
                    data: {'deploy_id': deploy_id, 'instance': instance, 'status': 'failed'},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/deploy/process/'
                    },
                    error: function(){
                        $('.failDeployProcess').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $('.btnGetEventRecord').on(
        'click', function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var event_id = $('[data-value=1]').parents('tr').find('td:nth-child(1)').text();
            var instance_id = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var group = $('[data-value=1]').parents('tr').find('td:nth-child(3)').text();
            var create_time = $('[data-value=1]').parents('tr').find('td:nth-child(5)').text();
            $.ajax(
                {
                    url: '/sengladmin/event/',
                    type: 'get',
                    data: {
                        'event_id': event_id,
                        'instance_id': instance_id,
                        'group': group,
                        'create_time': create_time,
                    },
                    success: function(resp){
                        if(resp.rsp_head.rsp_code == 200){
                            $('#event_id').val(resp.rsp_body.event.event_id)
                            $('#instance_id').val(resp.rsp_body.event.instance_id)
                            $('#group').val(resp.rsp_body.event.group)
                            $('#description').val(resp.rsp_body.event.description)
                            $('#additional').val(resp.rsp_body.event.additional)
                            $('#additional2').val(resp.rsp_body.event.additional2)
                            $('#additional3').val(resp.rsp_body.event.additional3)
                            $('#create_time').val(resp.rsp_body.event.create_time)
                        }
                    }
                }
            )
        }
    );

    $('#button_deploy').on(
        'click', function(){
            var datacenter_name = $('#datacenter').val();
            var service_name = $('#service').val();
            var group_name = $('#group').val();
            var version = $('#version').val();
            console.log(datacenter_name)
            console.log(service_name)
            console.log(group_name)
            console.log(version)
            $.ajax(
                {
                    url: '/sengladmin/deploy/',
                    type: 'post',
                    data: {'datacenter_name': datacenter_name, 'service_name': service_name, 'group_name': group_name, 'version': version},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/deploy/'
                    },
                    error: function(){
                        $('.removeDatacenter').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $(".btnPassService").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var status = $('[data-value=1]').parents('tr').find('td:nth-child(5)').text();
            if (status != 'waiting'){
                alert('该状态不需要进行审核')
                $(this).attr('data-target', '')
                return
            }
        }
    );

    $('#button_pass_testing').on(
        'click', function(){
            var service = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var version = $('[data-value=1]').parents('tr').find('td:nth-child(3)').text();
            $.ajax(
                {
                    url: '/sengladmin/testing/',
                    type: 'post',
                    data: {'service': service, 'version': version, 'status': 'pass'},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/testing/'
                    },
                    error: function(){
                        $('.passTesting').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );

    $(".btnRefuseService").on(
        'click',function(){
            $(this).attr('data-value',1).parents('tr').siblings().find("[data-toggle='modal']").attr('data-value',2);
            var status = $('[data-value=1]').parents('tr').find('td:nth-child(5)').text();
            if (status != 'waiting'){
                alert('该状态不需要进行审核')
                $(this).attr('data-target', '')
                return
            }
        }
    );

    $('#button_refuse_testing').on(
        'click', function(){
            var service = $('[data-value=1]').parents('tr').find('td:nth-child(2)').text();
            var version = $('[data-value=1]').parents('tr').find('td:nth-child(3)').text();
            $.ajax(
                {
                    url: '/sengladmin/testing/',
                    type: 'post',
                    data: {'service': service, 'version': version, 'status': 'refuse'},
                    success: function(resp){
                        alert(resp.rsp_head.rsp_info)
                        window.location.href = '/sengladmin/testing/'
                    },
                    error: function(){
                        $('.refuseTesting').on(
                            'hide.bs.modal', function(){
                                $(this).removeData()
                            }
                        )
                    }
                }
            )
        }
    );


});


function repass_verify(){
   var pwd1 = $("#register_password").val();
   var pwd2 = $("#repeat_password").val();
   var info = "";
   if (pwd1 == pwd2) {
       $("#submit_register").prop('disabled', false);
   }
   else {
       info = "<font color='red'>两次密码不相同</font>";
       $("#submit_register").prop('disabled', true);
   }
   $("#verify").html(info);
}

function modify_pass_verify(){
   var pwd1 = $("#new_password").val();
   var pwd2 = $("#repeat_password").val();
   var info = "";
   if (pwd1 == pwd2) {
       $("#button_submit").prop('disabled', false);
   }
   else {
       info = "<font color='red'>两次密码不相同</font>";
       $("#button_submit").prop('disabled', true);
   }
   $("#verify").html(info);
}

function S4() {
   return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
}

function guid() {
   return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}

function getVal() {
    var datacenterVal=null;
    var serviceVal=null;
    var groupVal=null;
    var arrVal=[0,0];

    $('#datacenter').change(function(){
        datacenterVal=$('#datacenter option:selected').val();
        if(datacenterVal!="" || datacenterVal!="undefined"){
            arrVal[0]=datacenterVal;
            postVal(arrVal);
        }
    });

    $('#service').change(function(){
        serviceVal=$('#service option:selected').val();
        if(serviceVal!="" || serviceVal!="undefined"){
            arrVal[1]=serviceVal;
            postVal(arrVal);
        }
    });
}

function postVal(arrVal){
    if(arrVal[0] !=0 && arrVal[1] !=0){
        console.log(arrVal)
        $.ajax({
            url: '/sengladmin/resource/condition/',
            type:'get',
            data:{'service': arrVal[1], 'datacenter': arrVal[0]},
            dataType:'json',
            success:function(resp){
                var group_html = '<option value="">NULL</option>';
                $.each(resp.rsp_body.groups, function(i, d) {
                    group_html += '<option value="' + d.name + '">' + d.name + '</option>'
                });
                $('#group').html(group_html);

                console.log(resp.rsp_body.versions)
                var version_html = '<option value="">NULL</option>';
                $.each(resp.rsp_body.versions, function(i, d) {
                    version_html += '<option value="' + d.version + '">' + d.version + '</option>'
                });
                $('#version').html(version_html);
                
            },
            error:function(xxh,type,error){
                console.log(error)
            }
        })
    }else{
        $('#group').html('');
        $('#version').html('');
    }
}

function reqDync() {
    $('#group').change(function(){
        groupVal=$('#group option:selected').val();
        if(groupVal!="" && groupVal!="undefined"){
            $.ajax({
                url: '/sengladmin/resource/condition/',
                type:'get',
                data:groupVal,
                dataType:'json',
                success:function(resp){
                    var version_html = '<option value="">NULL</option>';
                    $.each(resp.groups, function(i, d) {
                        version_html += '<option value="' + d.version + '">' + d.version + '</option>'
                    });
                    $('#version').html(version_html);
                },
                error:function(xxh,type,error){
                    console.log(error)
                }
            })
        }else{
            $('#version').html('');
        }
    });
}

$('tbody tr td').on(
    'mouseover',function () {
        var indexTd=$(this).index();
        $(this).parent().css('background','#d1e1ed').siblings().css('background','none');
        /*$('tbody tr').each(function () {
            $(this).find('td:eq('+indexTd+')').css('background','#d1e1ed').siblings().css('background','none');
        });*/
    }
);
