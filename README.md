![GitHub](https://img.shields.io/github/license/fathe4wiin/francinette-image) ![GitHub top language](https://img.shields.io/github/languages/top/fathe4wiin/francinette-image) ![GitHub repo size](https://img.shields.io/github/repo-size/fathe4wiin/francinette-image) ![GitHub Repo stars](https://img.shields.io/github/stars/fathe4wiin/francinette-image) ![GitHub repo directory count](https://img.shields.io/github/directory-file-count/fathe4wiin/francinette-image) ![GitHub watchers](https://img.shields.io/github/watchers/fathe4wiin/francinette-image) ![GitHub followers](https://img.shields.io/github/followers/fathe4wiin) ![GitHub contributors](https://img.shields.io/github/contributors/fathe4wiin/francinette-image) ![GitHub last commit (branch)](https://img.shields.io/github/last-commit/fathe4wiin/francinette-image/master)

<div align="right">
  👉
  <a href="https://github.com/fathe4wiin/francinette-image/blob/master/README.md">
    <img height="20px" src="https://github-production-user-asset-6210df.s3.amazonaws.com/25512932/282272296-82e81111-e524-439b-b971-900ce90d0603.png" alt="en">
  </a>
   <a href="https://github.com/fathe4wiin/francinette-image/blob/master/README_FR.md">
    <img height="20px" src="https://github-production-user-asset-6210df.s3.amazonaws.com/25512932/282272298-f8be0b14-1175-41e8-9ff9-91eb29c35779.png" alt="fr">
  </a>
  <a href="https://github.com/fathe4wiin/francinette-image/blob/master/README_ES.md">
    <img height="20px" src="https://github.com/user-attachments/assets/02babee0-5442-43f3-8062-71b946f3d62f" alt="es">
  </a>
</div>
<h1 align="center">Francinette install on <strong>42-Session-Ubuntu</strong></h1>

Francinette created by **[xicodomingues](https://github.com/xicodomingues)** is a tool to be able to test different projects of 42 (`libft`, `ft_printf`, `get_next_line`, `minitalk` and `pipex`).

Here is a simple installer that enables you to install Francinette on an **Ubuntu PC** within a **cluster of 42**  without `sudo` access. I would like to point out that I am not the creator of the Francinette! This is just a script that makes installation easier. Thanks to [xicodomingues](https://github.com/xicodomingues).

How does the installer work? It clones this fork. The test suites are already in this repository, under `francinette/tests`, and the installer copies them into place. It clones the francinette runner, then creates a Python virtualenv in `~/francinette/venv`. Packages, including norminette, are installed with that virtualenv's pip. Nothing is installed with `sudo`, and Docker is not used. `paco` and `francinette` run `tester.sh`, which activates that virtualenv.

After installation, use the `francinette` or `paco` command inside your project's directory to execute it.

> [!note]
> You need `python3` and `git` already on the session. The installer does not call `sudo` or `apt`. If `python3-venv` is missing, it falls back to [virtualenv.pyz](https://bootstrap.pypa.io/virtualenv.pyz), still without sudo.

## INSTALL:

Copy and paste the following line into your terminal to kick off the installation, and you'll be all set to start testing your school 42 projects with Francinette in no time!

```shell
bash -c "$(curl -fsSL https://raw.githubusercontent.com/fathe4wiin/francinette-image/master/install.sh)"
```

## Uninstall:

```shell
bash -c "$(curl -fsSL https://raw.githubusercontent.com/fathe4wiin/francinette-image/master/uninstall.sh)"
```
## Documentation

I can only advise you to look at the [original Francinette documentation](https://github.com/xicodomingues/francinette/tree/master#readme) for good use of this great tool!

## Who should I thank?

The suites under `francinette/tests` are part of this repository. This list is credit for the people who wrote them.

* [xicodomingues](https://github.com/xicodomingues) and [arsalas](https://github.com/arsalas) creator of the [francinette](https://github.com/xicodomingues/francinette) having link different tests, carried out by the people below
* [Tripouille](https://github.com/Tripouille) for [libftTester](https://github.com/Tripouille/libftTester), [gnlTester](https://github.com/Tripouille/gnlTester) and [printfTester](https://github.com/Tripouille/printfTester)
* [jtoty](https://github.com/jtoty) and [y3ll0w42](https://github.com/y3ll0w42) for [libft-war-machine](https://github.com/y3ll0w42/libft-war-machine)
* [alelievr](https://github.com/alelievr) for [libft-unit-test](https://github.com/alelievr/libft-unit-test) and [printf-unit-test](https://github.com/alelievr/printf-unit-test)
* [cacharle](https://github.com/cacharle) for [ft_printf_test](https://github.com/cacharle/ft_printf_test)
* [vfurmane](https://github.com/vfurmane) for [pipex-tester](https://github.com/vfurmane/pipex-tester)
* [gmarcha](https://github.com/gmarcha) for [pipexMedic](https://github.com/gmarcha/pipexMedic)
