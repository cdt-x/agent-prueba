"""Interfaz de usuario de consola con Rich."""

import sys
import os
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich import box
import time

# Configurar encoding UTF-8 para Windows
if sys.platform == "win32":
    os.system("chcp 65001 > nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class ConsoleUI:
    """Interfaz de usuario para el agente de ventas."""

    def __init__(self, agent_name: str = "FUTURE", company_name: str = "IAgentic Solutions"):
        self.console = Console(force_terminal=True)
        self.agent_name = agent_name
        self.company_name = company_name

    def show_welcome(self):
        """Muestra la pantalla de bienvenida."""
        self.console.clear()

        title = Text()
        title.append("+--------------------------------------------------------------+\n", style="cyan")
        title.append("|", style="cyan")
        title.append("          AGENTE VENDEDOR DE IA                              ", style="bold white")
        title.append("|\n", style="cyan")
        title.append("|", style="cyan")
        title.append(f"           {self.company_name}                              ", style="white")
        title.append("|\n", style="cyan")
        title.append("+--------------------------------------------------------------+", style="cyan")

        self.console.print(title)
        self.console.print()

    def show_agent_message(self, message: str):
        """Muestra un mensaje del agente."""
        panel = Panel(
            Markdown(message),
            title=f"[bold cyan]{self.agent_name}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()

    def show_user_message(self, message: str):
        """Muestra un mensaje del usuario."""
        panel = Panel(
            message,
            title="[bold green]Tú[/bold green]",
            border_style="green",
            padding=(0, 2)
        )
        self.console.print(panel)
        self.console.print()

    def get_user_input(self) -> str:
        """Obtiene input del usuario."""
        self.console.print("[bold yellow]>>> [/bold yellow]", end="")
        try:
            return input()
        except EOFError:
            return "salir"

    def show_thinking(self):
        """Muestra indicador de pensamiento."""
        with self.console.status(f"[cyan]{self.agent_name} está pensando...[/cyan]"):
            time.sleep(0.5)

    def show_typing_effect(self, message: str, delay: float = 0.02):
        """Muestra el mensaje con efecto de escritura."""
        panel_text = ""
        with Live(console=self.console, refresh_per_second=30) as live:
            for char in message:
                panel_text += char
                panel = Panel(
                    panel_text,
                    title=f"[bold cyan]{self.agent_name}[/bold cyan]",
                    border_style="cyan",
                    padding=(1, 2)
                )
                live.update(panel)
                time.sleep(delay)
        self.console.print()

    def show_profile_summary(self, profile: dict):
        """Muestra un resumen del perfil del cliente."""
        table = Table(title="Perfil del Cliente", box=box.ROUNDED)
        table.add_column("Campo", style="cyan")
        table.add_column("Valor", style="white")

        fields = [
            ("Nombre", profile.get("name", "No especificado")),
            ("Empresa", profile.get("company", "No especificada")),
            ("Industria", profile.get("industry", "No detectada")),
            ("Tipo", profile.get("customer_type", "Desconocido")),
            ("Etapa", profile.get("buying_stage", "Conocimiento")),
            ("Urgencia", profile.get("urgency", "Desconocida")),
            ("Engagement", f"{profile.get('engagement_score', 0):.0f}%"),
            ("Calificación", f"{profile.get('qualification_score', 0):.0f}%"),
        ]

        for field, value in fields:
            table.add_row(field, str(value) if value else "N/A")

        if profile.get("pain_points"):
            table.add_row("Problemas", ", ".join(profile["pain_points"][:3]))

        if profile.get("interested_products"):
            table.add_row("Intereses", ", ".join(profile["interested_products"][:3]))

        self.console.print(table)
        self.console.print()

    def show_products_menu(self, products: list):
        """Muestra el menú de productos."""
        table = Table(title="Catálogo de Productos", box=box.ROUNDED)
        table.add_column("#", style="cyan", width=3)
        table.add_column("Producto", style="white")
        table.add_column("Precio", style="green")
        table.add_column("Tiempo", style="yellow")

        for i, product in enumerate(products, 1):
            table.add_row(
                str(i),
                product["nombre"],
                product["precio_base"],
                product["tiempo_implementacion"]
            )

        self.console.print(table)
        self.console.print()

    def show_conversation_summary(self, summary: dict):
        """Muestra resumen de la conversación."""
        conv = summary.get("conversation", {})
        profile = summary.get("profile", {})

        self.console.print("\n[bold cyan]═══ Resumen de Conversación ═══[/bold cyan]\n")

        table = Table(box=box.SIMPLE)
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="white")

        table.add_row("Turnos totales", str(conv.get("total_turns", 0)))
        table.add_row("Fase actual", conv.get("current_phase", "N/A"))
        table.add_row("Engagement", f"{profile.get('engagement_score', 0):.0f}%")
        table.add_row("Calificación", f"{profile.get('qualification_score', 0):.0f}%")

        self.console.print(table)
        self.console.print()

    def show_help(self):
        """Muestra ayuda de comandos."""
        help_text = """
[bold cyan]Comandos disponibles:[/bold cyan]

[yellow]/productos[/yellow]  - Ver catálogo de productos
[yellow]/perfil[/yellow]     - Ver perfil del cliente actual
[yellow]/resumen[/yellow]    - Ver resumen de la conversación
[yellow]/reiniciar[/yellow]  - Reiniciar la conversación
[yellow]/salir[/yellow]      - Finalizar y salir

[dim]Escribe normalmente para conversar con el agente.[/dim]
"""
        self.console.print(Panel(help_text, title="Ayuda", border_style="yellow"))
        self.console.print()

    def show_error(self, message: str):
        """Muestra un mensaje de error."""
        self.console.print(f"[bold red]Error:[/bold red] {message}")
        self.console.print()

    def show_info(self, message: str):
        """Muestra un mensaje informativo."""
        self.console.print(f"[bold blue]Info:[/bold blue] {message}")
        self.console.print()

    def show_success(self, message: str):
        """Muestra un mensaje de éxito."""
        self.console.print(f"[bold green][OK][/bold green] {message}")
        self.console.print()

    def show_farewell(self, message: str):
        """Muestra mensaje de despedida."""
        panel = Panel(
            Markdown(message),
            title="[bold magenta]Despedida[/bold magenta]",
            border_style="magenta",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()

    def confirm(self, message: str) -> bool:
        """Pide confirmación al usuario."""
        self.console.print(f"[yellow]{message} (s/n):[/yellow] ", end="")
        response = input().lower().strip()
        return response in ["s", "si", "sí", "yes", "y"]
