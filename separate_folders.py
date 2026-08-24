

def separate_folders_by_level(folders_list:list):
    separated_paths = []
    paths_parents = {}

    pos = 0
    for folder in folders_list:
        math = (pos/len(folders_list))*100
        print(f"\rBuilding folders structure... ({math:.1f}%)",end="",flush=True)
        pos += 1

        parts = folder.split("/")[1:]
        build = ""
        root = -1

        for dir in parts:
            build += dir

            if build not in separated_paths:
                separated_paths.append(build)
                paths_parents[build] = root

                root = separated_paths.index(build)
            else:
                root = separated_paths.index(build)

            build += "/"

    if pos != 0:
        print("")

    return (separate_levels(separated_paths,paths_parents),separated_paths,paths_parents)


def separate_levels(paths:list,datalist:dict):
    levels = []
    val_list = [-1]

    path_indexes = {
        path: index
        for index, path in enumerate(paths)
    }

    pos = 0
    while True:
        print("\rSeparating folder hierarchy by levels"+("."*pos),end="",flush=True)
        pos += 1
        keys = []

        for val in val_list:
            keys = keys + [key for key, value in datalist.items() if value == val]

        if len(keys) == 0:
            break

        val_list = [path_indexes[dir_] for dir_ in keys]
        levels.append(val_list)
    
    print("")

    return levels