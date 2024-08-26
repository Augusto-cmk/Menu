import os
import platform
import signal

import readchar
from tabulate import tabulate


class Menu:
    def __init__(self, fluxo: dict, options: list[str], parameters: list = [], n_columns=3, insert_index=False,
                 end_with_select=False):
        """
        fluxo: dict map to indicate the function that have executed, when selected
        options: the list name of options of your function
        parameters: list of parameters that you may input on all of functions on the fluxo
        insert_index: insert the index of selection on the function
        end_with_select: end of Menu, with selected an option
        """
        signal.signal(signal.SIGINT, self.__exit)
        if platform.system() == 'Darwin':  # macOS
            self.enter, self.command = ('\r', 'clear')
            self.exit = 'exit'
        elif os.name == 'nt':  # Windows
            self.enter, self.command = ('\r', 'cls')
        else:  # Linux and others
            self.enter, self.command = ('\n', 'clear')
        self.fluxo = fluxo
        self.fluxo[len(fluxo.keys()) + 1] = self.__exit
        self.options = options
        self.options.append("Exit")
        self.selected_option = 0
        os.system(self.command)
        self.parameters = parameters
        self.execute = True
        self.insert_index = insert_index
        self.end_with_select = end_with_select
        self.n_columns = n_columns
        self.main()


    def __menu(self):
        os.system(self.command)
        controls = [
            ["W", "Move up"],
            ["A", "Move left"],
            ["S", "Move down"],
            ["D", "Move right"],
            ["Enter", "Select option"],
            ["E", "Show terminal function"],
            ["Q", "Exit"]
        ]

        num_options = len(self.options)
        column_height = (num_options + self.n_columns - 1) // self.n_columns

        # Criando a tabela para as opções
        options_table = [['' for _ in range(self.n_columns)] for _ in range(column_height)]
        for i in range(column_height):
            for j in range(self.n_columns):
                index = i + j * column_height
                if index < num_options:
                    option = self.options[index]
                    if index == self.__selected_option:
                        options_table[i][j] = f"\033[1;37;42m[*] {option}\033[m"
                    else:
                        options_table[i][j] = f"[ ] {option}"

        # Combinar tabelas lado a lado
        combined_table = []
        for i in range(max(len(controls), len(options_table))):
            control_row = controls[i] if i < len(controls) else ["", ""]
            options_row = options_table[i] if i < len(options_table) else [""] * self.n_columns
            combined_table.append(control_row + ["|"] + options_row)

        # Printando a tabela combinada
        header_options = ["" for i in range(len(self.options))]
        print(tabulate(combined_table, headers=["Key", "Action"] + ["|"] + header_options, tablefmt="simple_grid"))

    def main(self):
        num_options = len(self.options)
        column_height = (num_options + self.n_columns - 1) // self.n_columns
        while self.execute:
            self.__menu()
            key = readchar.readchar()
            if key == 'w':  # Sobe uma linha
                self.__selected_option = (self.__selected_option - 1) % num_options
            elif key == 's':  # Desce uma linha
                self.__selected_option = (self.__selected_option + 1) % num_options
            elif key == 'a':  # Move uma coluna à esquerda
                if self.__selected_option < column_height:
                    self.__selected_option = (self.__selected_option - column_height) % num_options
                else:
                    self.__selected_option -= column_height
            elif key == 'd':  # Move uma coluna à direita
                if self.__selected_option + column_height >= num_options:
                    self.__selected_option = (self.__selected_option + column_height) % num_options
                else:
                    self.__selected_option += column_height
            elif key == self.enter:
                if self.insert_index:
                    self.fluxo[self.selected_option + 1](self.selected_option, *self.parameters)
                    if self.end_with_select:
                        self.execute = False
                    if self.execute:
                        input("Any-> Voltar")
                else:
                    self.fluxo[self.selected_option + 1](*self.parameters)
                    if self.end_with_select:
                        self.execute = False
                    if self.execute:
                        input("Any-> Voltar")

    def __exit(self, *parameters):
        self.execute = False