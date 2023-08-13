import os
import re
import subprocess
import glob

regex = re.compile(r"\\input{(?P<filename>.*)}")
ex_files = ["0.macro.tex", "main.tex"]


def update_macro(filepath):
    ifile = open(filepath, "r")
    ofile = open(filepath + ".new", "w")

    for line in ifile:
        if line.startswith("%"):
            continue

        m = re.search(r".*(?P<rashmi>\\rashmi{.*?}.*)", line)
        if m:
            line = line.replace(m.group("rashmi"), "")

        m = re.search(r".*(?P<jason>\\jason{.*?}.*)", line)
        if m:
            line = line.replace(m.group("jason"), "")

        if r"\jupdate{" in line and "newcommand" not in line:
            line = line.replace(r"\jupdate", "")


        ofile.write(line)
    os.rename(filepath + ".new", filepath)


def pre_processing(filepath):
    update_macro(filepath)


def load_file(filepath):
    if not os.path.exists(filepath) and not filepath.endswith(".tex"):
        filepath = filepath + ".tex"

    with open(filepath) as ifile:
        return ifile.read()


def replace_input(input_line, dir_path):
    output = []

    match = regex.match(input_line)
    if match:
        filename = match.group("filename")
        filepath = "{}/{}".format(dir_path, filename)
        text = load_file(filepath).split("\n")
        for line in text:
            line = line.strip()
            if line.startswith("\\input"):
                line = replace_input(line, dir_path)

            output.append(line)
    else:
        print("cannot find input in {}".format(line))

    return "\n".join(output)


def concatenate(dir_path):
    mfile = open(dir_path + "/main.tex", "r")
    mfile_new = open(dir_path + "/main_concatenate.tex", "w")

    for line in mfile:
        line = line.strip()
        if line.startswith("%"):
            continue

        if line.strip().startswith("\\input"):
            line = replace_input(line, dir_path)

        # print(line)
        mfile_new.write("{}\n".format(line))


def latex_diff(draft, revision):
    concatenate(draft)
    concatenate(revision)
    subprocess.run("rm -rf {}_diff".format(draft), shell=True)
    subprocess.run("cp -r {} {}_diff".format(draft, draft), shell=True)
    subprocess.run(
        "latexdiff {} {} > {}_diff/main.tex".format(
            draft + "/main_concatenate.tex", revision + "/main_concatenate.tex", draft
        ),
        shell=True,
    )
    os.rename("{}/main_concatenate.tex".format(draft), "{}/main.tex".format(draft))


def latex_diff(draft, revision):
    subprocess.run("rm -rf {}_diff".format(draft), shell=True)
    subprocess.run("cp -r {} {}_diff".format(revision, draft), shell=True)
    subprocess.run("cp makefile {}_diff".format(draft), shell=True)
    subprocess.run("cp -r acmart.cls {}_diff".format(draft), shell=True)
    for f in glob.glob("{}/*.tex".format(draft)):
        should_skip = False
        for filename in ex_files:
            if filename in f:
                should_skip = True
                break
        if should_skip:
            continue

        pre_processing(f)
        pre_processing(f.replace(draft, revision))

        print(
            "latexdiff {} {} > {}".format(
                f, f.replace(draft, revision), f.replace(draft, draft + "_diff")
            )
        )
        subprocess.run(
            "latexdiff --preamble={}/0.macro.tex {} {} > {}".format(
                draft + "_diff",
                f,
                f.replace(draft, revision),
                f.replace(draft, draft + "_diff"),
            ),
            shell=True,
        )
        post_process(f.replace(draft, draft + "_diff"))

    with open("{}_diff/0.macro.tex".format(draft), "a") as ofile:
        ofile.write(
            r"""
%DIF PREAMBLE EXTENSION ADDED BY LATEXDIFF
%DIF UNDERLINE PREAMBLE %DIF PREAMBLE
\RequirePackage[normalem]{ulem} %DIF PREAMBLE
\RequirePackage{color}\definecolor{RED}{rgb}{1,0,0}\definecolor{BLUE}{rgb}{0,0,1} %DIF PREAMBLE
\providecommand{\DIFadd}[1]{{\protect\color{blue}\uwave{#1}}} %DIF PREAMBLE
\providecommand{\DIFdel}[1]{{\protect\color{red}\sout{#1}}}                      %DIF PREAMBLE
%DIF SAFE PREAMBLE %DIF PREAMBLE
\providecommand{\DIFaddbegin}{} %DIF PREAMBLE
\providecommand{\DIFaddend}{} %DIF PREAMBLE
\providecommand{\DIFdelbegin}{} %DIF PREAMBLE
\providecommand{\DIFdelend}{} %DIF PREAMBLE
%DIF FLOATSAFE PREAMBLE %DIF PREAMBLE
\providecommand{\DIFaddFL}[1]{\DIFadd{#1}} %DIF PREAMBLE
\providecommand{\DIFdelFL}[1]{\DIFdel{#1}} %DIF PREAMBLE
\providecommand{\DIFaddbeginFL}{} %DIF PREAMBLE
\providecommand{\DIFaddendFL}{} %DIF PREAMBLE
\providecommand{\DIFdelbeginFL}{} %DIF PREAMBLE
\providecommand{\DIFdelendFL}{} %DIF PREAMBLE
%DIF END PREAMBLE EXTENSION ADDED BY LATEXDIFF
"""
        )

    # subprocess.run("latexdiff {} {} > {}_diff/main.tex".format(draft + "/main_concatenate.tex", revision + "/main_concatenate.tex", draft), shell=True)
    # os.rename("{}/main_concatenate.tex".format(draft), "{}/main.tex".format(draft))


def post_process(filepath):
    start_phrase = r"~\DIFdelbegin \DIFdel{\mbox{%DIFAUXCMD"
    end_phrase = r"}\DIFdelend \DIFaddbegin \DIFadd{\mbox{%DIFAUXCMD"

    started = False
    ifile = open(filepath, "r")
    ofile = open(filepath + ".new", "w")
    for line in ifile:
        if start_phrase in line:
            line.replace(start_phrase, "")

        elif started:
            if end_phrase in line:
                started = False
                line.replace(end_phrase, "")
            else:
                continue
        
        m = re.search(r".*~\s*(?P<citation>\\DIFdelbegin \\DIFdel{\\cite{.*}}\\DIFdelend).*", line)
        if m:
            line = line.replace(m.group("citation"), "")

        m = re.search(r"(?P<pre>.*)\\DIFaddbegin\s*\\DIFadd{~?\s*(?P<post>\\cite.*)}\\DIFaddend", line)
        while m:
            line = m.group("pre") + m.group("post")
            m = re.search(r"(.*)\\DIFaddbegin\s*\\DIFadd{~?\s*(\\cite.*)}\\DIFaddend", line)

        ofile.write(line)
    os.rename(filepath + ".new", filepath)


if __name__ == "__main__":
    # concatenate("2023-SOSP-S3FIFO-CR")

    # pre_processing("test.tex")

    latex_diff("draft_path", "revision_path")

