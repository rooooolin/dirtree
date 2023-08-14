from typing import Any
import os
from pyecharts import options as opts
from pyecharts.charts import Page, Tree
from tqdm import tqdm
from pyecharts.globals import ThemeType
from pyecharts import options as opts
import argparse


def set_args():
    parser = argparse.ArgumentParser('')
    parser.add_argument(
        '--rawpaths', default='./inputs/test1/;./inputs/test2/', type=str, help='')
    parser.add_argument(
        '--max_depth', default=100, type=int, help='')
    parser.add_argument(
        '--output', default='./outputs/render.html', type=str, help='')
    return parser.parse_args()

class DirTree:
    def __init__(self,args) -> None:
        self.args = args

    def get_tree_datas(self,subdir_name,stats,depth=0, max_depth=float('inf')):
        if depth >= max_depth:
            return None
        tree = {}
        tree['name'] = f"{subdir_name} ({stats['files']},{self.convert_size(stats['size'])})"
        tree['children'] = []
        subdirs = stats['subdirectories']
        for subdir_name, subdir_stats in subdirs.items():
            subdir_tree = self.get_tree_datas(subdir_name,subdir_stats, depth + 1, max_depth)
            if subdir_tree:
                tree['children'].append(subdir_tree)

        if not tree['children']:
            tree.pop('children')
        
        return tree

    def build_tree(self,stats):
        tree_datas = self.get_tree_datas('RAW',stats,max_depth=self.args.max_depth)
        tree= Tree(init_opts=opts.InitOpts(theme=ThemeType.LIGHT,width="1800px", 
                    height="1000px"))
        tree.add("", 
                 data=[tree_datas],
                 orient="LR",
                 collapse_interval=2,
                 symbol_size=14,
                 leaves_label_opts= opts.LabelOpts(font_size=14)
                 )
        tree.set_global_opts(
                    title_opts=opts.TitleOpts(title="directory tree"),
                    
                    )
        tree.render(self.args.output)
       
        
        #make_snapshot(driver, 'render.html', 'chart.png')
    def convert_size(self,bytes):
        units = ['bytes', 'KB', 'MB', 'GB', 'TB']

        unit_index = 0
        while bytes >= 1024 and unit_index < len(units) - 1:
            bytes /= 1024
            unit_index += 1

        bytes = round(bytes, 2)

        return f"{bytes} {units[unit_index]}"

    def directory_stats(self,directory,parent=None):
        stats = {'files': 0, 'size': 0, 'subdirectories': {}, 'parent': parent}

        for root, subdirs, files in os.walk(directory):
            if root == directory:
                subdirs[:] = [d for d in subdirs if d != '.']
            
            subdir_stats = stats
            for subdir in os.path.relpath(root, directory).split(os.path.sep):
                subdir_stats = subdir_stats['subdirectories'].setdefault(subdir, {'files': 0, 'size': 0, 'subdirectories': {}, 'parent': subdir_stats})
            
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                subdir_stats['files'] += 1
                subdir_stats['size'] += file_size

                parent_stats = subdir_stats['parent']
                while parent_stats is not None:
                    parent_stats['files'] += 1
                    parent_stats['size'] += file_size
                    parent_stats = parent_stats.get('parent')

        if '.' in stats['subdirectories']:
            del stats['subdirectories']['.']

        return stats
    
    def merge_stats(self,dir1, dir2):
        merged = {}
        merged['subdirectories'] = {}
        merged['files'] = dir1['files'] + dir2['files']
        merged['size'] = dir1['size'] + dir2['size']

        subdirs1 = dir1['subdirectories']
        subdirs2 = dir2['subdirectories']

        for subdir_name, subdir1 in subdirs1.items():
            merged['subdirectories'][subdir_name] = subdir1
            if subdir_name in subdirs2:
                merged['subdirectories'][subdir_name] = self.merge_stats(subdir1, subdirs2[subdir_name])

        for subdir_name, subdir2 in subdirs2.items():

            
            if subdir_name not in merged['subdirectories']:
                merged['subdirectories'][subdir_name] = subdir2

        return merged

    def __call__(self, *args: Any, **kwds: Any) -> Any:

        all_stats={'files': 0, 'size': 0, 'subdirectories': {}, 'parent': None}
        for p in self.args.rawpaths:
            stats=self.directory_stats(p)
            all_stats = self.merge_stats(all_stats,stats)
        self.build_tree(all_stats)
        

if __name__=='__main__':
    args = set_args()
    args.rawpaths = args.rawpaths.split(';')
    DirTree(args)()