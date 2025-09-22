# Polymorphic Obfuscator + Syscalls Builder

Este projeto gera automaticamente executáveis C ofuscados e polimórficos, com stubs de syscalls dinâmicos no estilo SysWhispers3.

## Funcionalidades
- Polimorfismo completo: variáveis, funções, strings, junk code.
- Strings criptografadas via XOR.
- Hashing de APIs para esconder nomes.
- Geração automática de stubs inline syscalls com números reais de cada build do Windows.
- Teste automático pós-compilação.

## Estrutura
- base.c : código C de entrada.
- builder.py : polimorfisador e compilador.

## Uso
1. Crie seu código funcional em `base.c`.
2. Rode `python builder.py`.
3. Será gerado um `build_xxxxx.exe` pronto, funcional e diferente a cada build.

## Requisitos
- Python 3
- Biblioteca `pefile` (`pip install pefile`)
- MinGW (`x86_64-w64-mingw32-gcc`)
- Windows 64 bits

## Notas
Cada execução do builder gera binário diferente
