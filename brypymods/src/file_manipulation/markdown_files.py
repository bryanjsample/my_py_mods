r'''
    Module to convert any number of Markdown files to PDF files using github.com/Wandmalfarbe's pandoc template. "(https://github.com/Wandmalfarbe/pandoc-latex-template?tab=readme-ov-file)"

    External Dependencies:
        - Python
            - Getch : pip install getch
        - CLI Tools
            - texlive (Latex processor) : brew install texlive
            - cairo (vector graphics processor) : brew install cairo
            - pandoc (file converter) : brew install pandoc
        - Pandoc Eisvogel Latex Template
            - extract most recent zip file from : "https://github.com/Wandmalfarbe/pandoc-latex-template/releases/tag/2.4.2"
                - Will need to be moved into your pandoc templates directory!
                    - Unix / Linux / MacOS : "/Users/USERNAME/.local/share/pandoc/templates/"
                    - Windows Vista or later : "C:\Users\USERNAME\AppData\Roaming\pandoc\\templates"
'''
from file_manipulation.directory import Directory
from file_manipulation.get_keys import get_key_press
from typing import List
from time import sleep
import subprocess
import os


class MarkdownFile():
    '''Single Markdown file object'''
    def __init__(self, target_name:str, directory_path:str) -> None:
        '''
        Object representing a single markdown file.

        Doesn't fully inherit from MarkdownFiles, only the name and directory path are passed in as arguments.
        
        Properties:
            - self.Parent_Directory : path to parent directory of file object
            - self.Target_Name : file name of the targeted md file
            - self.Target_Path : path to targeted md file
            - self.Destination_Name : file name of the destination pdf file
            - self.Destination_Path : path to desination pdf file
        '''
        self._parent_directory = directory_path
        self._target_name = target_name
        self._target_path = f'{directory_path}/{target_name}'
        self._destination_name = target_name.replace('.md','.pdf')
        self._destination_path = f'{directory_path}/{self.Destination_Name}'


    @property
    def Parent_Directory(self) -> str:
        return self. _parent_directory

    @property
    def Target_Name(self) -> str:
        return self._target_name

    @property
    def Target_Path(self) -> str:
        return self._target_path

    @property
    def Destination_Name(self) -> str:
        return self._destination_name

    @property
    def Destination_Path(self) -> str:
        return self._destination_path

    def __str__(self):
        return f'File Name : {self.Target_Name}\nParent directory : {self.Parent_Directory}'

    def confirm_conversion(self) -> str:
        '''Confirm with enter key before converting.'''
        conversion_string = f'Attempting to convert {self.Target_Name}  ---->  {self.Destination_Name}...'
        print(conversion_string)
        confirmed = get_key_press(message=f'\n\n    ENTER : convert file to pdf\n    ANY OTHER KEY : continue without converting', pressed_enter=True, pressed_any_other=False)
        if confirmed:
            return conversion_string
        else:
            return False

    def open_pdf_file(self) -> None:
        '''
            Open pdf file in preview.
        '''
        subprocess.run(['open', '-g', self.Destination_Path])
        os.system('clear')

    def convert_single_md_to_pdf(self, converted_files:dict) -> None:
        '''Convert target markdown file to a pdf of the same name.'''
        os.system('clear')
        conversion_string = self.confirm_conversion()
        if not conversion_string:
            return
        print(f'\n{conversion_string:^50}'.replace('Attempting to convert', 'Converting'))
        self.conversion(converted_files)
        open_confirmed = get_key_press(message=f'\nFinished converting {self.Destination_Name}.\n\n    ENTER : open pdf\n    ANY OTHER KEY : continue without opening\n', pressed_enter=True, pressed_any_other=False)
        if open_confirmed:
            self.open_pdf_file()
    
    def convert_all_md_to_pdf(self, converted_files:dict) -> None:
        '''Convert target markdown file to a pdf of the same name.'''
        print(f'Converting {self.Target_Name} ----> {self.Destination_Name}')
        self.conversion(converted_files)
        print(f'Finished converting {self.Destination_Name}\n\n')

    def conversion(self, converted_files:dict) -> None:
        try:
            subprocess.check_call(['pandoc', self.Target_Path, '-o', self.Destination_Path, '--from', 'markdown', '--template', 'eisvogel', '--highlight-style', 'tango'])
            converted_files[self.Target_Name] = self.Destination_Name
        except subprocess.CalledProcessError:
            get_key_press(message=f'\n\n{self.Target_Name} failed to convert.\n\n    ENTER : continue converting files\n    ANY OTHER KEY : quit')

class MarkdownFiles(Directory):
    '''
        Converts one or more Markdown Files to PDF using pandoc after inheriting attributes
        from directory.py's Directory class.
    '''
    def __init__(self, echo_dir_contents_at_init:bool=True):
        '''Inherit properties from directory and obtain list of target markdown file objects.

            Properties
                - self.Target_Extension: 'md'
                - self.Directory_Path : string of the absolute path to the directory
                - self.Changed_Directory: defaults to false, only changed to true if a new path is used
                - self.Files: list containing files targeted
                - self.File_Dict: dictionary to select one file from many, only needed if there is > 1 file
                - self.Target_Files: list of individual MarkdownFiles

            Example Instantiation:
                from file_manipulation import MarkDownFiles\n
                mdfiles = MarkdownFiles()\n
                mdfiles.convert_files()\n
        '''
        Directory.__init__(self, welcome_message_command='convert', target_extension='md', echo_dir_contents_at_init=echo_dir_contents_at_init)
        self._target_files:List[MarkdownFile]

    @property
    def Target_Files(self) -> List[MarkdownFile]:
        return self._target_files
    
    @Target_Files.setter
    def Target_Files(self, list_files) -> None:
        self._target_files = list_files

    def __str__(self) -> str:
        '''
            Markdown Files : file1.md, file2.md, file3.md, ...
            Parent Directory : /path/to/markdown/files
        '''
        return f"Markdown Files : {', '.join(self.Target_Files)}\nParent Directory : {self.Directory_Path}"

    def finished_converting(self) -> None:
        '''Once finished converting, print all files that successfully converted'''
        if len(self.converted_files.keys()) == 0:
            print('No md were converted.\n')
        else:
            tar_width = max([len(x) for x in self.converted_files.keys()])
            print(f'Finished processing all md files in {self.Directory_Path}.\n')
            for target, destination in self.converted_files.items():
                print(f'    {target:>{tar_width}} ----> {destination}')

    def convert_files(self) -> None:
        self.converted_files:dict = {}
        # os.system('clear')
        convert_one_at_a_time = get_key_press(message='\nAttempting to convert markdown files to pdf format...\n\n    ENTER : converts all md files\n    ANY OTHER KEY : converts only select md files one at a time', pressed_enter=False, pressed_any_other=True)
        if convert_one_at_a_time:
            self.Target_Files = [MarkdownFile(x, self.Directory_Path) for x in self.choose_multiple_items()]
            for mdfile in self.Target_Files:
                mdfile.convert_single_md_to_pdf(self.converted_files)
        elif not convert_one_at_a_time:
            os.system('clear')
            self.Target_Files = [MarkdownFile(x, self.Directory_Path) for x in self.Files]
            for mdfile in self.Target_Files:
                mdfile.convert_all_md_to_pdf(self.converted_files)
        os.system('clear')
        self.finished_converting()
