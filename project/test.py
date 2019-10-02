import estcp_project.work as w

wd = w.WorkDir('../test/test/test')


#print(w.WorkDir.is_work_dir(wd.dir))
#print(w.WorkDir.is_work_dir(wd.dir/'.ipynb_checkpoints'))
#print(list(wd.get_dvc_files()))

#print(wd.reltodir())

print(list(w.find_WorkDirs()))
