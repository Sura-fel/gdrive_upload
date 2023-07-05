import os, argparse
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive



dont_upload = [
	'venv',
	'.git',
	'.gitignore',
	'tmp',
	'.ipynb_checkpoint'
]


class Uplaoder:
	def autherize_gdrive(self):
		gauth = GoogleAuth()
		gauth.LoadCredentialsFile("mycreds.txt")
		
		if gauth.credentials is None:
			gauth.GetFlow()
			gauth.flow.params.update({'access_type': 'offline'})
			gauth.flow.params.update({'approval_prompt': 'force'})
			gauth.LocalWebserverAuth()
			
		elif gauth.access_token_expired:
			gauth.Refresh()
		
		else:
			gauth.Authorize()
		
		gauth.SaveCredentialsFile("mycreds.txt")
		global drive
		drive = GoogleDrive(gauth)
		return 0
		
	def create_folder(self, parent_id,name):
		new_folder = drive.CreateFile({
			'title': name,
			"parents": [{"kind": "drive#fileLink", "id": parent_id}],
			"mimeType": "application/vnd.google-apps.folder"
		})
		new_folder.Upload()
		return new_folder
	
	def create_file(self, folder_id, file):
		file_upload = drive.CreateFile({
			"parents": [{"kind": "drive#fileLink", "id": folder_id}]
		})
		file_upload.SetContentFile(file)
		file_upload.Upload()
		return file_upload
	
	def check(self,parent='root'):
		x =  f" '{parent}' in parents and trashed=false"
		backed = drive.ListFile({'q': x}).GetList()
		print('q : Quit \n.. : Root Folder')
		
		for j,i in enumerate(backed):
			print(f'{j}: {i["title"]} : {i["id"]}')
		
		z = input(': ')
		if z.lower() == 'q':
			return 0
			
		elif z == '..':
			self.check()
			
		else:
			try:
				self.check(backed[int(z)]['id'])
			
			except:
				print('Invalid option')
			

	def upload(self,parent, path):
		x =  f"'{parent}' in parents and trashed=false"
		backed = drive.ListFile({'q': x}).GetList()
		bck = [file['title'].lower() for file in backed]
		print(bck)
		
		for entry in os.scandir(path):
			if entry.name.lower() in dont_upload:
				continue
				
			elif entry.name.lower() in bck: 
				print(f'{entry.path} exists')
				if entry.is_dir():
					a = bck.index(entry.name.lower())
					fol = backed[a]
					self.upload(fol['id'], entry.path)
			
			elif entry.is_file():
				file = self.create_file(parent,entry.path)
				print( f'{file["title"]} uploaded')
			
			elif entry.is_dir():
				fol = self.create_folder(parent, entry.name.lower())
				print( f'new folder {fol["title"]} id : {fol["id"]}')
				self.upload(fol['id'],entry.path)
	
	def delete_non(self,parent, path='.'):
		x =  f"'{parent}' in parents and trashed=false"
		backed = drive.ListFile({'q': x}).GetList()
		unt = [i.name.lower() for i in os.scandir(path)]
		
		for trs in backed:
			
			if not (trs['title'].lower() in unt):
				print(f'if {trs["title"]}')
				
				if input(f'delete {trs["title"]}?[y/n]: ').lower() == 'y':
					file_id = trs['id']
					drive.CreateFile({'id': file_id}).Trash()
				
				else:
					print(f'if else trs["title"]')
					continue;
			
			elif ['mimeType'] == 'application/vnd.google-apps.folder':
					print(f'elif {trs["title"]}')
					path = path + '/' + trs["title"]
					self.delete_non(trs['id'],path)
					path = '/'.join((path.split("/")[:-1]))
			
			else:
				print(f'else {trs["title"]}')
				continue

			
parser = argparse.ArgumentParser()
parser.add_argument('-u', '--upload', type=str, nargs=2, help = " -u <folder_id> <path>")
parser.add_argument('-d', '--delete', type=str, nargs=2, help = " -d <folder_id> <path>")
parser.add_argument('-c', '--check', action='store_true')

args = parser.parse_args()

me = Uplaoder()
me.autherize_gdrive()

if args.upload:
	folder_id, path = args.upload
	print(folder_id,type(folder_id))
	print(path,type(path))
	me.upload(folder_id, path)
	
elif args.delete:
	folder_id, path = args.delete
	me.delete_non(folder_id, path)
	
elif args.check:
	me.check()