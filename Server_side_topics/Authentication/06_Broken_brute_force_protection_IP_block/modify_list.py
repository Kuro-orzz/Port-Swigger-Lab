
usernames = open('./../common_username.txt', 'r', encoding='utf-8').read().strip().split('\n')
passwords = open('./../common_password.txt', 'r', encoding='utf-8').read().strip().split('\n')


new_user_list = []
new_pass_list = []


def modify_list():
    for idx, password in enumerate(passwords):
        if idx % 2 == 0:
            new_user_list.append('wiener')
            new_pass_list.append('peter')
        new_user_list.append('carlos')
        new_pass_list.append(password)
    
    with open('modified_user_list.txt', 'w', encoding='utf-8') as output:
        for username in new_user_list:
            output.write(username + '\n')
        
    with open('modified_pass_list.txt', 'w', encoding='utf-8') as output:
        for password in new_pass_list:
            output.write(password + '\n')

modify_list()