import os
import database
import packages
import threading
from logger import log
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.exceptions import HTTPException


# SET ENV
POSTGRES_URL = os.environ.get('POSTGRES_URL', 'postgres')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'python')
POSTGRES_PW = os.environ.get('POSTGRES_PW', 'python')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'package-management')
TIMEOUT_DB_INIT = int(os.environ.get('TIMEOUT_DB_INIT', 15))
APP_VERSION = os.environ.get('APP_VERSION', '0.0.0')
APP_ENV = os.environ.get('APP_ENV', 'DEBUG')

DB = database.DB(POSTGRES_DB, POSTGRES_USER, POSTGRES_PW, POSTGRES_URL, TIMEOUT_DB_INIT)
PACKAGES = packages.PACKAGES(DB)
app = Flask(__name__)


# UPDATING YUM AND RPM CACHES
thread_job = threading.Thread(target=PACKAGES.update_yum_cache)
thread_job.start()


# ROOT PAGE
@app.route('/', methods=['GET', 'POST'])
def index():
    data_prod = DB.select_db_all("packages_prod")
    data_qa = DB.select_db_all("packages_qa")
    data_dev = DB.select_db_all("packages_dev")
    version_color_prod = PACKAGES.version_comparison('prod')
    version_color_qa = PACKAGES.version_comparison('qa')
    version_color_dev = PACKAGES.version_comparison('dev')
    env = request.args.get('env')

    if env == "prod" or env == "qa" or env == "dev":
        return render_template(
                    "index.html",
                    data_prod=data_prod,
                    data_qa=data_qa,
                    data_dev=data_dev,
                    env=env,
                    green_list_prod=version_color_prod,
                    green_list_qa=version_color_qa,
                    green_list_dev=version_color_dev,
                    APP_VERSION=APP_VERSION
                )
    else:
        return render_template(
                    "index.html",
                    data_prod=data_prod,
                    data_qa=data_qa,
                    data_dev=data_dev,
                    env="prod",
                    green_list_prod=version_color_prod,
                    green_list_qa=version_color_qa,
                    green_list_dev=version_color_dev,
                    APP_VERSION=APP_VERSION
                )


# PACKAGES MANAGMENT FUNCTION
@app.route('/packages', methods=['GET', 'POST'])
def packages_action():
    # getting action parameter value
    action = request.args.get('action')
    # getting env parameter value (pord/qa/dev)
    env = request.args.get('tabs')

    # ADD NEW PACKAGE TO DB
    if action == "add_package":
        data_prod = DB.select_db_all("packages_prod")
        data_qa = DB.select_db_all("packages_qa")
        data_dev = DB.select_db_all("packages_dev")
        env = request.args.get('tabs')
        submit = request.args.get('submit')

        if env == "prod":
            db_table = "packages_"+env
            if submit == "save":
                uniq_value = 'True'
                _package_name = request.args.get('text_pack_name')
                _current_version = request.args.get('text_cur_ver')
                try:
                    _search_repo_version = request.args.get('checkbox_rep_ver')
                except HTTPException as http_error:
                    _search_repo_version = http_error
                if _search_repo_version == "search_repo_version":
                    _repo_version = PACKAGES.check_version_in_repo(_package_name)
                else:
                    _repo_version = "not_found"
                for item in data_prod:
                    if item[1] == _package_name:
                        uniq_value = 'False'
                        break
                    else:
                        uniq_value = 'True'
                if uniq_value == "True":
                    insert_string = (
                        f"'{_package_name}','{_current_version}', '{_repo_version}'"
                    )
                    DB.insert_db(
                            db_table,
                            "package_name,current_version,repo_version",
                            insert_string
                        )
                    data_prod = DB.select_db_all(
                                        "packages_prod"
                                    )
                    return render_template(
                                "index.html",
                                data_prod=data_prod,
                                data_qa=data_qa,
                                data_dev=data_dev,
                                env=env,
                                add_package=env,
                                APP_VERSION=APP_VERSION
                            )
                elif uniq_value == "False":
                    return render_template(
                                "error.html",
                                _package_name=_package_name,
                                APP_VERSION=APP_VERSION,
                                error_type="package_name"
                            )
                else:
                    return render_template(
                                "error.html",
                                APP_VERSION=">>> DEBUG: else uniq_value exception"
                            )
            else:
                return render_template(
                            "index.html",
                            data_prod=data_prod,
                            data_qa=data_qa,
                            data_dev=data_dev,
                            env=env,
                            add_package=env,
                            APP_VERSION=APP_VERSION
                        )

        elif env == "qa":
            db_table = "packages_"+env
            if submit == "save":
                uniq_value = 'True'
                _package_name = request.args.get('text_pack_name')
                _current_version = request.args.get('text_cur_ver')
                try:
                    _search_repo_version = request.args.get('checkbox_rep_ver')
                except HTTPException as http_error:
                    _search_repo_version = http_error
                if _search_repo_version == "search_repo_version":
                    _repo_version = PACKAGES.check_version_in_repo(_package_name)
                else:
                    _repo_version = "not_found"
                for item in data_qa:
                    if item[1] == _package_name:
                        uniq_value = 'False'
                        break
                    else:
                        uniq_value = 'True'
                if uniq_value == "True":
                    insert_string = (
                        f"'{_package_name}', '{_current_version}', '{_repo_version}'"
                    )
                    DB.insert_db(
                            db_table,
                            "package_name,current_version,repo_version",
                            insert_string
                        )
                    data_qa = DB.select_db_all("packages_qa")
                    return render_template(
                                "index.html",
                                data_prod=data_prod,
                                data_qa=data_qa,
                                data_dev=data_dev,
                                env=env,
                                add_package=env,
                                APP_VERSION=APP_VERSION
                            )
                elif uniq_value == "False":
                    return render_template(
                                "error.html",
                                _package_name=_package_name,
                                APP_VERSION=APP_VERSION,
                                error_type="package_name"
                            )
                else:
                    return render_template(
                                "error.html",
                                APP_VERSION=">>> DEBUG: else uniq_value exception"
                            )
            else:
                return render_template(
                            "index.html",
                            data_prod=data_prod,
                            data_qa=data_qa,
                            data_dev=data_dev,
                            env=env,
                            add_package=env,
                            APP_VERSION=APP_VERSION
                        )

        elif env == "dev":
            db_table = "packages_"+env
            if submit == "save":
                uniq_value = 'True'
                _package_name = request.args.get('text_pack_name')
                _current_version = request.args.get('text_cur_ver')
                try:
                    _search_repo_version = request.args.get('checkbox_rep_ver')
                except HTTPException as http_error:
                    _search_repo_version = http_error
                if _search_repo_version == "search_repo_version":
                    _repo_version = PACKAGES.check_version_in_repo(_package_name)
                else:
                    _repo_version = "not_found"
                for item in data_dev:
                    if item[1] == _package_name:
                        uniq_value = 'False'
                        break
                    else:
                        uniq_value = 'True'
                if uniq_value == "True":
                    insert_string = (
                        f"'{_package_name}', '{_current_version}', '{_repo_version}'"
                    )
                    DB.insert_db(
                            db_table,
                            "package_name,current_version,repo_version",
                            insert_string
                        )
                    data_dev = DB.select_db_all("packages_dev")
                    return render_template(
                                "index.html",
                                data_prod=data_prod,
                                data_qa=data_qa,
                                data_dev=data_dev,
                                env=env,
                                add_package=env,
                                APP_VERSION=APP_VERSION
                            )
                elif uniq_value == "False":
                    return render_template(
                                "error.html",
                                _package_name=_package_name,
                                APP_VERSION=APP_VERSION,
                                error_type="package_name"
                            )
                else:
                    return render_template(
                                "error.html",
                                APP_VERSION=">>> DEBUG: else uniq_value exception")
            else:
                return render_template(
                            "index.html",
                            data_prod=data_prod,
                            data_qa=data_qa,
                            data_dev=data_dev,
                            env=env,
                            add_package=env,
                            APP_VERSION=APP_VERSION
                        )

        else:
            return render_template(
                        "error.html",
                        APP_VERSION=">>> DEBUG: else action=add_package (ENV not set)"
                    )

    # GENEARATED HASH STRING WITH PACKAGE_NAME AND VERSION
    elif action == "generate_hash":
        data_prod = DB.select_db_all("packages_prod")
        data_qa = DB.select_db_all("packages_qa")
        data_dev = DB.select_db_all("packages_dev")
        if env == "prod":
            hash_string_prod = []
            for item in data_prod:
                hash_string_prod.append(f"{item[1]}:{item[2]}")
            return render_template(
                        "index.html",
                        hash_string_prod=hash_string_prod,
                        data_prod=data_prod,
                        data_qa=data_qa,
                        data_dev=data_dev,
                        env='prod',
                        gen_hash_block="SHOW",
                        APP_VERSION=APP_VERSION,
                        popup='show'
                    )
        elif env == "qa":
            hash_string_qa = []
            for item in data_qa:
                hash_string_qa.append(f"{item[1]}:{item[2]}")
            return render_template(
                        "index.html",
                        hash_string_qa=hash_string_qa,
                        data_prod=data_prod,
                        data_qa=data_qa,
                        data_dev=data_dev,
                        env='qa',
                        gen_hash_block="SHOW",
                        APP_VERSION=APP_VERSION,
                        popup='show'
                    )
        elif env == "dev":
            hash_string_dev = []
            for item in data_dev:
                hash_string_dev.append(f"{item[1]}:{item[2]}")
            return render_template(
                        "index.html",
                        hash_string_dev=hash_string_dev,
                        data_prod=data_prod,
                        data_qa=data_qa,
                        data_dev=data_dev,
                        env='dev',
                        gen_hash_block="SHOW",
                        APP_VERSION=APP_VERSION,
                        popup='show'
                    )
        else:
            return render_template(
                        "error.html"
                    )

    # REMOVED PACKAGE TO DB
    elif action == "remove_package":
        db_table = "packages_"+request.args.get('env')
        db_table_id = "'"+request.args.get('index')+"'"
        DB.delete_db(
                db_table,
                db_table_id
        )
        return redirect(
                    url_for(
                        '.index',
                        env=request.args.get('env')
                    )
                )

    # UPDATE SELECTED PACKAGES REPO VERSIONS -> CURRENT VERSION
    elif action == "update_version":
        db_table = "packages_"+request.args.get('env')
        db_table_id = "id = '"+request.args.get('index')+"'"
        db_table_current_version = "'"+request.args.get('new_version')+"'"
        if index == "all_ids":
            data = DB.select_db_all(db_table)
            for item in data:
                new_version = "'"+item[3]+"'"
                item_id = "id = "+str(item[0])
                DB.update_db(
                        db_table,
                        'current_version',
                        new_version,
                        item_id
                    )
            return redirect(
                        url_for(
                            '.index',
                            env=request.args.get('env')
                        )
                    )
        else:
            DB.update_db(
                    db_table,
                    'current_version',
                    db_table_current_version,
                    db_table_id
                )
            return redirect(
                        url_for(
                            '.index',
                            env=request.args.get('env')
                        )
                    )

    # UPDATE ALL PACKAGES REPO VERSIONS -> CURRENT VERSION
    elif action == "update_versions_packages":
        env = request.args.get('tabs')
        db_table = "packages_"+env
        data = DB.select_db_all(db_table)
        for item in data:
            new_version = "'"+item[3]+"'"
            item_id = "id = "+str(item[0])
            DB.update_db(
                    db_table,
                    'current_version',
                    new_version,
                    item_id
                )
        return redirect(
                    url_for(
                        '.index',
                        env=request.args.get('tabs')
                    )
                )

    # SEARCH FOR LATEST VERSIONS OF ALL PACKAGES IN YUM REPOSITORIES AND UPDATE VALUES IN THE DB
    elif action == "check_repo_versions":
        PACKAGES.update_yum_cache()
        data_prod = DB.select_db_all("packages_prod")
        data_qa = DB.select_db_all("packages_qa")
        data_dev = DB.select_db_all("packages_dev")
        for item in data_prod:
            pkg_version = PACKAGES.check_version_in_repo(item[1])
            item_id = f"id = {item[0]}"
            DB.update_db(
                    'packages_prod',
                    'repo_version',
                    pkg_version,
                    item_id
                )
        for item in data_qa:
            pkg_version = PACKAGES.check_version_in_repo(item[1])
            item_id = "id = "+str(item[0])
            DB.update_db(
                    'packages_qa',
                    'repo_version',
                    pkg_version,
                    item_id
                )
        for item in data_dev:
            pkg_version = PACKAGES.check_version_in_repo(item[1])
            item_id = "id = "+str(item[0])
            DB.update_db(
                    'packages_dev',
                    'repo_version',
                    pkg_version,
                    item_id
                )
        return redirect(
                    url_for(
                        '.index',
                        env=request.args.get('tabs')
                    )
                )
    else:
        return render_template(
                    "error.html",
                    APP_VERSION=">>> DEBUG: /packages 'action not set'"
                )


# IMPORT PACKAGES PER HASH STRING FUNCTION
@app.route('/import', methods=['GET', 'POST'])
def import_packages():
    env = request.form.get('env')
    submit = request.form.get('submit')
    hash_string = request.form.get('hash_string')
    log.info(
        f"app.route: {request.url}, method: {request.method}, parameters: {request.form.lists}"
    )
    if submit == "import":
        hash_string = hash_string.replace("[", "").replace("]", "").replace('"', '').replace("'", "").split(',')
        log.warning(type(hash_string))
        log.warning(hash_string)
        import_status_list = []
        for item in hash_string:
            log.warning(item)
            package = item.split(":")
            package_name = package[0]
            current_version = f"'{package[1]}'"
            repo_version = PACKAGES.check_version_in_repo(package_name)

            if env == "prod":
                db_table = "packages_"+env
            elif env == "qa":
                db_table = "packages_"+env
            elif env == "dev":
                db_table = "packages_"+env
            else:
                error_type = "import_env"
                return render_template(
                            "error.html",
                            error_type=error_type,
                            APP_VERSION=APP_VERSION
                        )

            insert_string = f"'{package_name}',{current_version},'{repo_version}'"
            DB.insert_db(
                db_table,
                "package_name,current_version,repo_version",
                insert_string
            )
            status = "package imported successfully"
            import_status = f"{package_name} {current_version} {repo_version} >>> {status}"
            import_status_list.append(import_status)

        return render_template(
                    "import_packages.html",
                    APP_VERSION=APP_VERSION,
                    stdout=import_status_list,
                    textarea_stdout='show'
                )
    else:
        return render_template(
                    "import_packages.html",
                    APP_VERSION=APP_VERSION
                )


# IMPORT OR ADD CUSTOM REPOSTIRIES FOR PACKAGES
@app.route('/repository', methods=['GET', 'POST'])
def repository_action():
    data_yum = PACKAGES.mount_yum_repos()
    data_rpm = PACKAGES.mount_rpm_repos()
    submit = request.form.get('submit')
    # tabs = request.form.get('tabs')
    log.info(
        f"app.route: {request.url}, method: {request.method}, parameters: {request.form.lists}"
    )

    # POST FOR ADD NEW REPOSITORY CONTENT
    if request.method == "POST":
        # adding yum content in file
        if submit == "add_yum":
            _repo_name = request.form['text_repo_name']
            _repo_content = request.form['text_repo_content']
            uniq_value = 'True'
            for item in data_yum:
                if item[1] == _repo_name:
                    uniq_value = 'False'
                    error_type = "repo_name"
                    break

            if uniq_value == "True":
                insert_values = "'"+_repo_name+"'"+","+"'"+_repo_content+"'"
                DB.insert_db('yum_repos_d', 'name,content', insert_values)
                PACKAGES.mount_yum_repos()
                return redirect("/repository")
            elif uniq_value == "False":
                return render_template(
                            "error.html",
                            _repo_name=_repo_name,
                            error_type=error_type,
                            APP_VERSION=APP_VERSION
                        )

        # ADD RPM PACKAGE LINK
        elif submit == "add_rpm":
            _rpm_name = request.form['text_rpm_name']
            _rpmurl = request.form['text_rpmurl']
            data_rpm = DB.select_db_all('rpm_list')
            uniq_value = 'True'
            for item in data_rpm:
                if item[2] == _rpmurl:
                    uniq_value = 'False'
                    error_type = "rpmurl"
                    break
                else:
                    uniq_value = 'True'
            if uniq_value == "True":
                insert_string = "'"+_rpm_name+"'"+","+"'"+_rpmurl+"'"
                DB.insert_db("rpm_list", "name,url", insert_string)
                PACKAGES.mount_rpm_repos()
                return redirect("/repository")
            elif uniq_value == "False":
                return render_template(
                            "error.html",
                            _rpmurl=_rpmurl,
                            error_type=error_type,
                            APP_VERSION=APP_VERSION
                        )

    # GET FOR LOADING PAGE AND SHOW INFO
    elif request.method == "GET":
        add_repo = request.args.get('add_repo')
        if add_repo == "add_yum":
            add_yum_enabled = "true"
            add_rpm_enabled = "false"
            show_add_rpm_button = "true"
            show_add_yum_button = "false"
        elif add_repo == "add_rpm":
            add_rpm_enabled = "true"
            add_yum_enabled = "false"
            show_add_rpm_button = "false"
            show_add_yum_button = "true"
        else:
            add_rpm_enabled = "false"
            add_yum_enabled = "false"
            show_add_rpm_button = "true"
            show_add_yum_button = "true"
        return render_template(
                    "repository.html",
                    data_yum=data_yum,
                    data_rpm=data_rpm,
                    APP_VERSION=APP_VERSION,
                    add_yum_enabled=add_yum_enabled,
                    add_rpm_enabled=add_rpm_enabled,
                    show_add_rpm_button=show_add_rpm_button,
                    show_add_yum_button=show_add_yum_button
                )


if __name__ == "__main__":
    if APP_ENV == "PROD":
        app.config.update(
            DEBUG=False,
            TESTING=False,
            DEVELOPMENT=False,
            CSRF_ENABLED=True,
            SECRET_KEY='1',
        )
        app.run(debug=False, host='0.0.0.0')
    else:
        app.config.update(
            DEBUG=True,
            TESTING=True,
            CSRF_ENABLED=True,
            DEVELOPMENT=True,
            SECRET_KEY='1',
        )
        app.run(debug=True, host='0.0.0.0')
