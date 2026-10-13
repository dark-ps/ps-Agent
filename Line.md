Пожалуйста, загрузите шрифт проекта. Если вы используете Termux, скопируйте и вставьте этот текст в окно терминала: 

```
pkg install -y curl tar fontconfig-utils && rm -rf ~/fonts && mkdir -p ~/fonts ~/.local/share/fonts ~/.termux && curl -L https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.tar.xz -o ~/fonts/font.tar.xz && tar -xJf ~/fonts/font.tar.xz -C ~/fonts && find ~/fonts -type f -name '*.ttf' -exec cp {} ~/.local/share/fonts/ \; && FONT="$(find ~/.local/share/fonts -type f -iname '*JetBrainsMono*NerdFont*Mono*Regular.ttf' | head -n1)" && cp "$FONT" ~/.termux/font.ttf && fc-cache -fv && termux-reload-settings
```

Если вы используете другой терминал/систему, измените команду. 