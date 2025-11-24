from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional
import uuid


class Category(Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    HEALTH = "health"
    EDUCATION = "education"
    OTHER = "other"


class Expense:
    def __init__(self, description: str, amount: float, category: Category, expense_date: date):
        if not description or not description.strip():
            raise ValueError("Description cannot be empty")
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if not isinstance(category, Category):
            raise ValueError("Invalid category")
        if expense_date > date.today():
            raise ValueError("Expense date cannot be in the future")

        self.id = str(uuid.uuid4())
        self.description = description.strip()
        self.amount = amount
        self.category = category
        self.date = expense_date

    def __repr__(self):
        return f"Expense({self.description}, ${self.amount}, {self.category.value}, {self.date})"


class ExpensePlanner:
    """
    Класс для управления личными финансами и планирования расходов
    """

    def __init__(self):
        self._expenses: List[Expense] = []
        self._category_budgets: Dict[Category, float] = {}
        self._monthly_budget: float = 0.0
        self._initialize_category_budgets()

    def _initialize_category_budgets(self) -> None:
        """Инициализация бюджетов для всех категорий"""
        for category in Category:
            self._category_budgets[category] = 0.0

    def add_expense(self, description: str, amount: float, category: Category, expense_date: date) -> str:
        """
        Добавление нового расхода

        Args:
            description: Описание расхода
            amount: Сумма расхода
            category: Категория расхода
            expense_date: Дата расхода

        Returns:
            ID созданного расхода
        """
        expense = Expense(description, amount, category, expense_date)
        self._expenses.append(expense)
        return expense.id

    def remove_expense(self, expense_id: str) -> bool:
        """
        Удаление расхода по ID

        Args:
            expense_id: ID расхода для удаления

        Returns:
            True если расход удален, False если не найден
        """
        if not expense_id:
            raise ValueError("Expense ID cannot be empty")

        initial_count = len(self._expenses)
        self._expenses = [exp for exp in self._expenses if exp.id != expense_id]
        return len(self._expenses) < initial_count

    def set_monthly_budget(self, budget: float) -> None:
        """
        Установка месячного бюджета

        Args:
            budget: Сумма месячного бюджета
        """
        if budget < 0:
            raise ValueError("Budget cannot be negative")
        self._monthly_budget = budget

    def set_category_budget(self, category: Category, budget: float) -> None:
        """
        Установка бюджета для конкретной категории

        Args:
            category: Категория расходов
            budget: Бюджет для категории
        """
        if not isinstance(category, Category):
            raise ValueError("Invalid category")
        if budget < 0:
            raise ValueError("Budget cannot be negative")

        self._category_budgets[category] = budget

    def get_total_expenses(self, start_date: date, end_date: date) -> float:
        """
        Получение общей суммы расходов за период

        Args:
            start_date: Начальная дата периода
            end_date: Конечная дата периода

        Returns:
            Общая сумма расходов за период
        """
        if not start_date or not end_date:
            raise ValueError("Dates cannot be None")
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")

        total = 0.0
        for expense in self._expenses:
            if start_date <= expense.date <= end_date:
                total += expense.amount
        return total

    def get_expenses_by_category(self, category: Category) -> List[Expense]:
        """
        Получение всех расходов по категории

        Args:
            category: Категория для фильтрации

        Returns:
            Список расходов указанной категории
        """
        if not isinstance(category, Category):
            raise ValueError("Invalid category")

        return [exp for exp in self._expenses if exp.category == category]

    def get_remaining_monthly_budget(self, year: int, month: int) -> float:
        """
        Расчет оставшегося бюджета на месяц

        Args:
            year: Год
            month: Месяц (1-12)

        Returns:
            Оставшийся бюджет
        """
        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12")

        start_date = date(year, month, 1)
        # Расчет последнего дня месяца
        if month == 12:
            end_date = date(year, month, 31)
        else:
            end_date = date(year, month + 1, 1)
            end_date = end_date.replace(day=end_date.day - 1)

        total_expenses = self.get_total_expenses(start_date, end_date)
        return self._monthly_budget - total_expenses

    def is_category_budget_exceeded(self, category: Category) -> bool:
        """
        Проверка превышения бюджета категории

        Args:
            category: Категория для проверки

        Returns:
            True если бюджет превышен, иначе False
        """
        if not isinstance(category, Category):
            raise ValueError("Invalid category")

        category_budget = self._category_budgets[category]
        if category_budget == 0:
            return False

        category_expenses = sum(exp.amount for exp in self.get_expenses_by_category(category))
        return category_expenses > category_budget

    def get_category_statistics(self, start_date: date, end_date: date) -> Dict[Category, float]:
        """
        Получение статистики расходов по категориям за период

        Args:
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            Словарь с суммами по категориям
        """
        if not start_date or not end_date:
            raise ValueError("Dates cannot be None")

        statistics = {}
        for expense in self._expenses:
            if start_date <= expense.date <= end_date:
                statistics[expense.category] = statistics.get(expense.category, 0.0) + expense.amount
        return statistics

    def get_top_expenses(self, limit: int) -> List[Expense]:
        """
        Получение самых крупных расходов

        Args:
            limit: Количество возвращаемых расходов

        Returns:
            Список самых крупных расходов
        """
        if limit <= 0:
            raise ValueError("Limit must be positive")

        sorted_expenses = sorted(self._expenses, key=lambda x: x.amount, reverse=True)
        return sorted_expenses[:limit]

    def get_expenses_summary(self) -> Dict:
        """
        Получение сводки по всем расходам

        Returns:
            Словарь со сводной информацией
        """
        total_expenses = sum(exp.amount for exp in self._expenses)
        avg_expense = total_expenses / len(self._expenses) if self._expenses else 0

        return {
            "total_expenses": total_expenses,
            "expense_count": len(self._expenses),
            "average_expense": avg_expense,
            "monthly_budget": self._monthly_budget,
            "category_budgets": self._category_budgets.copy()
        }

    # Property методы для доступа к данным
    @property
    def expenses(self) -> List[Expense]:
        return self._expenses.copy()

    @property
    def monthly_budget(self) -> float:
        return self._monthly_budget

    def get_category_budget(self, category: Category) -> float:
        return self._category_budgets[category]