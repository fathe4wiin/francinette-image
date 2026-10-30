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
<h1 align="center">Instalación de Francinette en <strong>42-Session-Ubuntu</strong></h1>

Francinette, creada por **[xicodomingues](https://github.com/xicodomingues)**, es una herramienta para testear distintos proyectos de 42 (`libft`, `ft_printf`, `get_next_line`, `minitalk` y `pipex`).

Este es un instalador simple que te permite instalar Francinette en un **PC Ubuntu** en un **clúster de 42**, sin acceso a `sudo`. Cabe destacar que no soy el creador de Francinette. ¡Esto es solo un script para facilitar la instalación! Gracias a [xicodomingues](https://github.com/xicodomingues).

¿Cómo funciona el instalador? Clona este fork. Las suites de tests ya están en este repositorio, en `francinette/tests`, y el instalador las copia en su sitio. Clona el lanzador de francinette y crea un virtualenv de Python en `~/francinette/venv`. Los paquetes, incluida norminette, se instalan con el pip de ese virtualenv. No usa `sudo` ni Docker. `paco` y `francinette` ejecutan `tester.sh`, que activa ese virtualenv.

Después de instalarlo, utiliza el comando `francinette` o `paco` en el directorio de tu proyecto para ejecutarlo.

> [!note]
> Hacen falta `python3` y `git` ya instalados. El instalador no llama a `sudo` ni a `apt`. Si falta `python3-venv`, usa [virtualenv.pyz](https://bootstrap.pypa.io/virtualenv.pyz), también sin sudo.

## Instalación:

Copia y pega la siguiente línea en tu terminal para iniciar la instalación, y estarás listo para comenzar a probar tus proyectos de la escuela 42 con Francinette en poco tiempo:

```shell
bash -c "$(curl -fsSL https://raw.githubusercontent.com/fathe4wiin/francinette-image/master/install.sh)"
```

## Desinstalación:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/fathe4wiin/francinette-image/master/uninstall.sh)"
```

## Documentación:

Te recomiendo encarecidamente consultar la documentación [original de Francinette](https://github.com/xicodomingues/francinette/tree/master#readme) para un buen uso de esta magnífica herramienta.

## ¿A quién debo agradecer?

Las suites en `francinette/tests` forman parte de este repositorio. Esta lista es solo el crédito.

* [xicodomingues](https://github.com/xicodomingues) y [arsalas](https://github.com/arsalas) creadores de [francinette](https://github.com/xicodomingues/francinette), con enlaces a diferentes pruebas realizadas por las personas que se mencionan a continuación.
* [Tripouille](https://github.com/Tripouille) por [libftTester](https://github.com/Tripouille/libftTester), [gnlTester](https://github.com/Tripouille/gnlTester) and [printfTester](https://github.com/Tripouille/printfTester)
* [jtoty](https://github.com/jtoty) y [y3ll0w42](https://github.com/y3ll0w42) por [libft-war-machine](https://github.com/y3ll0w42/libft-war-machine)
* [alelievr](https://github.com/alelievr) por [libft-unit-test](https://github.com/alelievr/libft-unit-test) y [printf-unit-test](https://github.com/alelievr/printf-unit-test)
* [cacharle](https://github.com/cacharle) por [ft_printf_test](https://github.com/cacharle/ft_printf_test)
* [vfurmane](https://github.com/vfurmane) por [pipex-tester](https://github.com/vfurmane/pipex-tester)
* [gmarcha](https://github.com/gmarcha) por [pipexMedic](https://github.com/gmarcha/pipexMedic)
