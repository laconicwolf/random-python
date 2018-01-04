def form_auth_creds():
    creds = {'aris connect': ['/copernicus/default/service/login',
                             {'schema': '0', 'alias': 'superuser', 'password': 'superuser'},
                             {'schema': '0', 'alias': 'system', 'password': 'manager'}],
             'lan': ['/goform/home_loggedout',
                    {'loginUsername': 'admin', 'loginPassword': 'password'},
                    {'loginUsername': 'admin', 'loginPassword': 'admin'}]
            }
    
    return creds
   

def basic_auth_creds():
    creds = [{'admin': 'admin'},
             {'admin': 'password'}]
    
    return creds

def main():
    print(form_auth_creds())
    print(basic_auth_creds())

    
if __name__ == '__main__':
    main()