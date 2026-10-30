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
<h1 align="center">Installation de la Francinette sur <strong>une session de 42 Ubuntu</strong></h1>


La Francinette, créée par **[xicodomingues](https://github.com/xicodomingues)** est un outil permettant de tester différents projets de l'école 42 tels que `libft`, `ft_printf`, `get_next_line`, `minitalk` et `pipex`.

Voici un installateur simple qui vous permet d'installer la Francinette sur un **ordinateur Ubuntu** au sein d'un **cluster de l'école 42** sans avoir besoin des privilèges `sudo`. Je tiens à souligner que je ne suis pas le créateur de la Francinette ! Il s'agit simplement d'un script qui facilite l'installation. Merci à [xicodomingues](https://github.com/xicodomingues).

Comment fonctionne cet installateur ? Il clone ce fork. Les suites de tests sont déjà dans ce dépôt, sous `francinette/tests`, et l'installateur les copie en place. Il clone le lanceur francinette, puis crée un virtualenv Python dans `~/francinette/venv`. Les paquets, y compris norminette, sont installés avec le pip de ce virtualenv. Aucune commande `sudo` ou Docker n'est utilisée. `paco` et `francinette` lancent `tester.sh`, qui active ce virtualenv.

Après l'installation, utilisez la commande `francinette` ou `paco` à l'intérieur du dossier de votre projet pour l'exécuter.

> [!note]
> `python3` et `git` doivent déjà être présents. L'installateur n'appelle ni `sudo` ni `apt`. Si `python3-venv` manque, il utilise [virtualenv.pyz](https://bootstrap.pypa.io/virtualenv.pyz), toujours sans sudo.

## INSTALLATION :

Copiez et collez la ligne suivante dans votre terminal pour lancer l'installation, et vous serez prêt à commencer à tester vos projets de l'école 42 avec Francinette en un rien de temps !

```shell
bash -c "$(curl -fsSL https://raw.githubusercontent.com/fathe4wiin/francinette-image/master/install.sh)"
```

## DÉSINSTALLER:

```shell
bash -c "$(curl -fsSL https://raw.githubusercontent.com/fathe4wiin/francinette-image/master/uninstall.sh)"
```

## Documentation

Je vous conseille vivement de consulter la [documentation originale de Francinette](https://github.com/xicodomingues/francinette/tree/master#readme) pour bien utiliser cet excellent outil !

## Qui dois-je remercier ?

Les suites sous `francinette/tests` font partie de ce dépôt. Cette liste sert uniquement de crédit.

* [xicodomingues](https://github.com/xicodomingues) et [arsalas](https://github.com/arsalas) créateur de la [francinette](https://github.com/xicodomingues/francinette) ayant lié différents tests, réalisés par les personnes ci-dessous
* [Tripouille](https://github.com/Tripouille) pour [libftTester](https://github.com/Tripouille/libftTester), [gnlTester](https://github.com/Tripouille/gnlTester) et [printfTester](https://github.com/Tripouille/printfTester)
* [jtoty](https://github.com/jtoty) et [y3ll0w42](https://github.com/y3ll0w42) pour [libft-war-machine](https://github.com/y3ll0w42/libft-war-machine)
* [alelievr](https://github.com/alelievr) pour [libft-unit-test](https://github.com/alelievr/libft-unit-test) et [printf-unit-test](https://github.com/alelievr/printf-unit-test)
* [cacharle](https://github.com/cacharle) pour [ft_printf_test](https://github.com/cacharle/ft_printf_test)
* [vfurmane](https://github.com/vfurmane) pour [pipex-tester](https://github.com/vfurmane/pipex-tester)
* [gmarcha](https://github.com/gmarcha) pour [pipexMedic](https://github.com/gmarcha/pipexMedic)
