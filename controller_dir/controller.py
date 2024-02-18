from model_dir.model import engine, UserDb, UserPosts
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()


# CREATING THE USER PARAMETERS
################################################################################
class User:
    
    '''This class will take all the parameters needed for shaping the User.
    Such as password, email and name.
    This class will be called by the SystemManagement class and the final user
    will not have access to it.'''
    
    def _get_name(self) -> str:
        while True:
            try:
                name = str(input('Enter your name: ')).capitalize().strip()
                for letter in name:
                    if not letter.isalpha() and not letter.isspace():
                        print('\033[31mPlease, only type letters.\033[m')
                        raise ValueError
            except:
                continue
            else:
                return name

    def __set_name(self) -> None:
        self.name = self._get_name()

    def _get_email(self) -> str:
        while True:
            email = str(input('Enter your email: ')).lower().strip()
            if email == '' or len(email) < 5: 
                print('\033[31mPlease, type a valid email address.\033[m')
                continue
            elif not '@' in email:
                email += '@gmail.com'
            return email
    
    def __set_email(self) -> None:
        while True:
            email = self._get_email()
            exists = lambda x: session.query(UserDb).filter(UserDb.email == email).first()
            check = exists(email)
            session.close()
            if check == None: 
                self.email = email
                break
            print(f'\033[31mEMAIL ALREADY EXISTS, PLEASE CHOOSE A NEW ONE\033[m')
            continue

    def _get_password(self, text) -> str:
        import re
        from hashlib import sha256
        import getpass
        while True:
            password = getpass.getpass(prompt=f'{text}', stream=None)
            if len(password) < 8:
                print('\033[31mYour password MUST have at least 8 characteres.\033[m')
                continue
            elif not re.search("[a-z]", password):
                print('\033[31mYour password MUST have at least one lower case letter.\033[m')
                continue
            elif not re.search("[A-Z]", password):
                print('\033[31mYour password MUST have at least one upper case letter.\033[m')
                continue
            elif not re.search("[0-9]", password):
                print('\033[31mYour password MUST have at least one number.\033[m')
                continue
            else:
                encrypted_password = sha256(password.encode())
                return encrypted_password.hexdigest()

    def __set_password(self) -> None:
        self.password = self._get_password('Type your password: ')

    def _check_email(self) -> bool:
        given_email = self._get_email()
        exists = lambda x: session.query(UserDb).filter(
            UserDb.email == given_email).first()
        check = exists(given_email)
        session.close()
        if check != None: return check.id
        return 0

    def create_user(self) -> None:
        self.__set_name()
        self.__set_email()
        self.__set_password()

    def _encrypt_password(self) -> str:
        from hashlib import sha256
        import getpass
        password = getpass.getpass(prompt='Type your password: ', stream=None)
        encrypt_password = sha256(password.encode()).hexdigest()
        return encrypt_password


# CREATING THE SYSTEM MANAGEMENT THAT RECEIVES THE USER DATA
################################################################################
class SystemManagement:
   
    '''This class will register the parameters acquired by the User's Class and
    make the CRUD (Create, Read, Update, Delete) operations with it.
    There is a module called Sign In, in case the user is already registered
    they can access their Social Media Menu to post, read and delete data.'''
   
    def register(self, user_data: UserDb) -> None:
        try:
            user = UserDb(name=user_data.name,
                        email=user_data.email,
                        password=user_data.password)
            session.add(user)
        except:
            print(f'\033[31m{user_data.name} NOT ADDED\033[m')
            session.rollback()
        else:
            print(f'\033[32m{user_data.name} ADDED SUCCESSFULLY\033[m')
            session.commit()
        finally:
            session.close()

    def delete(self) -> str:
        id = User()._check_email()
        if id != 0:
            try:
                data = session.query(UserDb).filter(UserDb.id==id).first()
                password = User()._encrypt_password()
                if data.password != password: raise ValueError
                session.delete(data)
            except:
                print('\033[31mWRONG PASSWORD\033[m')
                session.rollback()
            else:
                print(f'\033[31m{data.name} SUCCESSFULLY DELETED\033[m')
                self.__delete_social_media(data.id)
                session.commit()
            finally:
                session.close()
        else:
            print('\033[31mUSER NOT FOUND.\033[m')

    def __delete_social_media(self, id) -> None:
        try:
            session.query(UserPosts).filter(UserPosts.id == id).delete()
            session.commit()
        except:
            session.rollback()
            pass
        finally:
            
            session.close()

    def change_password(self) -> None:
        id = User()._check_email()
        if id != 0:
            try:
                data = session.query(UserDb).filter(UserDb.id == id).first()
                password = User()._encrypt_password()
                if password == data.password:
                    new_password = User()._get_password('Type the new password: ')
                    data.password = new_password
                    print('\033[32mPASSWORD CHANGED SUCCESSFULLY\033[m')
                    session.commit()
                else:
                    raise ValueError
            except:
                print('\033[31mYOUR PASSWORDS DO NOT MATCH\033[m')
                session.rollback()
            finally:
                session.close()
        else:
            print('\033[31mEMAIL NOT FOUND\033[m')

    def sign_in(self) -> None:
        id = User()._check_email()
        if id != 0:
            try:
                data = session.query(UserDb).filter(UserDb.id == id).first()
                password = User()._encrypt_password()
                if password != data.password:
                    raise ValueError
                else:
                    session.close()
                    menu = Menu()
                    menu.menu_sm(data)
            except:
                print('\033[31mWRONG PASSWORD\033[m')
                session.rollback()
                session.close()
        else:
            print('\033[31mEMAIL NOT FOUND\033[m')
            menu = Menu()
            menu.main()


# CREATING A SOCIAL MEDIA PLATFORM FOR USERS TO POST THEIR THOUGHTS
################################################################################
class SocialMedia:
    '''This class will manage the posts related to a user, saving them into a 
    database with the user's ID as the primary key. Users will be able to read, 
    insert, and delete posts related to them. Access to this class is granted 
    only when authenticated using the correct user's email and password.'''

    def post(self, user: UserDb) -> None:
        text = str(input('What is on your mind: '))
        try:
            post_sm = UserPosts(user_id=user.id, posts=text)
            session.add(post_sm)
        except:
            session.rollback()
        else:
            print('\033[32mSUCCESSFULLY POSTED\033[m')
            session.commit()
        finally:
            session.close()

    def read_posts(self, user: UserDb) -> str:
        try:
            data = session.query(UserPosts).filter(UserPosts.user_id == user.id).all()
            if data == []: raise IndexError
            post_number = 1
            print(f'\033[1;42m{"POST":^5}|{"CONTENT":^50}\033[m')
            for line in data:
                print(f'{post_number:^5}| {line.posts:<50}')
                post_number += 1
        except:
            print('\033[31mYOU DO NOT HAVE POSTS. SHARE SMTH WITH US FIRST.\033[m')
        finally:
            session.close()


    def delete_posts(self, user: UserDb) -> None:
        try:
            keys = []
            data = session.query(UserPosts).filter(UserPosts.user_id == user.id).all()
            if data == []: raise IndexError
            post_number = 1
            for line in data:
                keys.append({'pk': line.id, 'number': post_number})
                post_number += 1
            self.__deleting_by_id(self.__receive_post_number(keys))
        except:
            print('\033[31mYOU DO NOT HAVE POSTS. SHARE SMTH WITH US FIRST.\033[m')
        finally:
            session.close()

    def __deleting_by_id(self, id) -> None:
        try:
            session.query(UserPosts).filter(UserPosts.id == id).delete()
            session.commit()
        except:
            session.rollback()
            print('\033[31mNOT DELETED\033[m')
        else:
            print('\033[32mSUCCESSFULLY DELETED.\033[m')
        finally:
            session.close()

    def __receive_post_number(self, numbers: list) -> int:
        right = False
        while True:
            try:
                chosen_post = int(input('Type the chosen number: '))
                for lines in numbers:
                    if lines['number'] == chosen_post: right = True
                if not right: raise IndexError
            except ValueError: print('\033[31mTYPE A NUMBER\033[m')
            except: 
                print('\033[31mCHOOSE A VALID POST\033[m')
            else:
                return chosen_post
            
# CREATING THE MENU
################################################################################
class Menu:
    '''This will be the Class that will interact with the final User. They will
    not have access to the rest of the data but the Menu Class. In case a User
    is not authenticated, they will return to the Main Menu.'''
    def main(self) -> str:
        system_management = SystemManagement()
        while True:
            print(f'''\033[1;42m{"MAIN MENU":^55}\033[m
[1] Register User
[2] Delete User
[3] Change Password
[4] Sign In
[5] Quit''')
            try:
                choice = int(input('Choose an option: '))
                assert 1 <= choice <= 5
            except:
                print('\033[31mINVALID OPTION\033[m')
            else:
                match choice:
                    case 1:
                        user = User()
                        user.create_user()
                        system_management.register(user)
                    case 2: system_management.delete()
                    case 3: system_management.change_password()
                    case 4: system_management.sign_in()
                    case 5:
                        print('See you soon...')
                        break

    def menu_sm(self, user) -> None:
        social_media = SocialMedia()
        while True:
            print(f'''\033[1;42m{f"{user.name.upper()} MENU":^55}\033[m
[1] POST
[2] READ POSTS
[3] DELETE POST
[4] QUIT''')
            try:
                choice = int(input('Choose an option: '))
                assert 1 <= choice <= 5
            except:
                print('\033[31mINVALID OPTION\033[m')
                menu = Menu()
                menu.main()
            else:
                match choice:
                    case 1: social_media.post(user)
                    case 2: social_media.read_posts(user)
                    case 3: social_media.delete_posts(user)
                    case 4: 
                        print('Returning you to the main menu...')
                        break
