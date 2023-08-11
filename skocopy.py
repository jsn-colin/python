import io
import json
import os
import sys
import tarfile


def usage():
    print("""
    Usage:
            {0} copy 旧tar包名 新tar包名:镜像名称:镜像版本
            {0} move 旧tar包名 新tar包名:镜像名称:镜像版本
            {0} show 镜像tar包
            
    example:
            {0} copy nginx-latest.tar nginx-1.17.1.tar:nginx:1.17.1         
            {0} move nginx-latest.tar nginx-1.17.1.tar:nginx:1.17.1 
            {0} show nginx-latest.tar
    """.format(sys.argv[0]))


def new_member_info(member, content):
    new_member = tarfile.TarInfo(member.name)
    new_member.size = len(content)
    new_member.mode = member.mode
    new_member.mtime = member.mtime
    new_member.type = member.type
    new_member.linkname = member.linkname
    new_member.uid = member.uid
    new_member.gid = member.gid
    new_member.uname = member.uname
    new_member.gname = member.gname

    return new_member


def sko_copy(source_tarfile, dest_tarfile, image_name, image_version):
    tar = tarfile.open(source_tarfile, "r:")
    new_tar = tarfile.open(dest_tarfile, "w:")
    for member in tar.getmembers():
        f = tar.extractfile(member)
        print("copy file ..." + member.name)
        if member.name == "repositories":
            content = f.read().decode()
            old_image_name = next(iter(json.loads(content)))
            old_image_version = next(iter(json.loads(content).get(old_image_name)))
            new_content = content.replace(old_image_name, image_name, 1)
            new_content = new_content.replace(old_image_version, image_version, 1)
            new_member = new_member_info(member, new_content)

            new_tar.addfile(new_member, fileobj=io.BytesIO(new_content.encode()))

        elif member.name == "manifest.json":
            content = f.read().decode()
            old_image_name_and_old_image_version = json.loads(content)[0].get("RepoTags")[0]
            new_image_name_and_new_image_version = image_name + ":" + image_version
            new_content = content.replace(old_image_name_and_old_image_version, new_image_name_and_new_image_version)
            new_member = new_member_info(member, new_content)

            new_tar.addfile(new_member, fileobj=io.BytesIO(new_content.encode()))

        else:
            new_tar.addfile(member, fileobj=f)

    tar.close()
    new_tar.close()


def sko_move(source_tarfile, dest_tarfile, image_name, image_version):
    sko_copy(source_tarfile, dest_tarfile, image_name, image_version)
    os.remove(source_tarfile)


def sko_show(tar_file):
    tar = tarfile.open(tar_file, "r:")
    have_repo_file = have_mani_file = False
    for member in tar.getmembers():
        if member.name == "repositories":
            have_repo_file = True
            f = tar.extractfile(member)
            content = f.read().decode()
            repositories_image_name = next(iter(json.loads(content)))
            repositories_image_version = next(iter(json.loads(content).get(repositories_image_name)))

        elif member.name == "manifest.json":
            have_mani_file = True
            f = tar.extractfile(member)
            content = f.read().decode()
            manifest_image_name_and_image_version = json.loads(content)[0].get("RepoTags")[0]
        else:
            continue
    if not all([have_repo_file, have_mani_file]):
        print("this is not docker images file")
    else:
        repositories_name = repositories_image_name + ":" + repositories_image_version
        manifest_name = manifest_image_name_and_image_version
        if manifest_name == repositories_name:
            print("imageName: %s" % repositories_name)
        else:
            print("different :repositoriesName: %s , manifestName: %s" %(repositories_name, manifest_name))


def main():
    if len(sys.argv) == 1 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
        usage()
    else:
        if sys.argv[1] in ["copy", "cp"]:
            oldImageTar = sys.argv[2]
            newImageTar, newImageName, newImageVersion = sys.argv[3].split(":")
            sko_copy(oldImageTar, newImageTar, newImageName, newImageVersion)

        elif sys.argv[1] in ["show"]:
            sko_show(sys.argv[2])
        elif sys.argv[1] in ["move", "mv"]:
            oldImageTar = sys.argv[2]
            newImageTar, newImageName, newImageVersion = sys.argv[3].split(":")
            sko_move(oldImageTar, newImageTar, newImageName, newImageVersion)
        else:
            usage()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("tips: param error!")
        print(e)
        usage()
