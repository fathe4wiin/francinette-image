FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

LABEL maintainer="mmorot@student.42lyon.fr"
LABEL version="1.0.3"
LABEL description="francinette image 42"


RUN apt update -y
RUN apt install git -y
WORKDIR /
RUN git clone --recursive https://github.com/xicodomingues/francinette.git
RUN apt update -y
RUN apt upgrade -y
RUN apt install gcc clang libpq-dev libbsd-dev libncurses-dev valgrind build-essential nasm clang ghc cmake make libxext-dev libbsd-dev libpq-dev -y
RUN apt install python3-dev python3-pip -y
RUN apt install python3-dev python3-venv python3-wheel -y
RUN python3 -m venv /francinette/venv
RUN /francinette/venv/bin/pip install --upgrade pip wheel
WORKDIR /francinette
RUN /francinette/venv/bin/pip install -r requirements.txt
RUN /francinette/venv/bin/pip install norminette
RUN find /francinette -name '*.py' -exec sed -i 's/from pipes import quote/from shlex import quote/g' {} +
COPY francinette/ /francinette/
COPY scripts/drop_libft_bonus_rule.py /tmp/drop_libft_bonus_rule.py
RUN python3 /tmp/drop_libft_bonus_rule.py
RUN chmod 755 tester.sh
CMD ["/francinette/tester.sh"]
