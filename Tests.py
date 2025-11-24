import pytest
from datetime import date, timedelta
from Main import ExpensePlanner, Category, Expense


class TestExpensePlanner:
    """Тесты для класса ExpensePlanner"""

    @pytest.fixture
    def planner(self):
        """Фикстура для создания экземпляра планировщика"""
        return ExpensePlanner()

    @pytest.fixture
    def sample_expenses(self, planner):
        """Фикстура с тестовыми расходами"""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Добавляем тестовые расходы
        expense1_id = planner.add_expense("Lunch", 25.50, Category.FOOD, yesterday)
        expense2_id = planner.add_expense("Bus ticket", 5.0, Category.TRANSPORT, today)
        expense3_id = planner.add_expense("Movie", 15.0, Category.ENTERTAINMENT, today)

        return {
            'food_id': expense1_id,
            'transport_id': expense2_id,
            'entertainment_id': expense3_id
        }

    # Тест 1: Добавление валидного расхода
    @pytest.mark.basic
    @pytest.mark.expense_management
    def test_add_valid_expense(self, planner):
        """Тест добавления валидного расхода"""
        expense_id = planner.add_expense("Test expense", 100.0, Category.FOOD, date.today())

        assert expense_id is not None
        assert len(planner.expenses) == 1

        expense = planner.expenses[0]
        assert expense.description == "Test expense"
        assert expense.amount == 100.0
        assert expense.category == Category.FOOD

    # Тест 2: Добавление расхода с невалидными данными (исключение)
    @pytest.mark.exception
    @pytest.mark.expense_management
    def test_add_expense_invalid_data(self, planner):
        """Тест добавления расхода с невалидными данными"""
        with pytest.raises(ValueError, match="Description cannot be empty"):
            planner.add_expense("", 100.0, Category.FOOD, date.today())

        with pytest.raises(ValueError, match="Amount must be positive"):
            planner.add_expense("Test", -50.0, Category.FOOD, date.today())

        with pytest.raises(ValueError, match="Expense date cannot be in the future"):
            future_date = date.today() + timedelta(days=1)
            planner.add_expense("Test", 100.0, Category.FOOD, future_date)

    # Тест 3: Удаление существующего расхода
    @pytest.mark.basic
    @pytest.mark.expense_management
    def test_remove_existing_expense(self, planner, sample_expenses):
        """Тест удаления существующего расхода"""
        initial_count = len(planner.expenses)
        result = planner.remove_expense(sample_expenses['food_id'])

        assert result is True
        assert len(planner.expenses) == initial_count - 1

    # Тест 4: Удаление несуществующего расхода
    @pytest.mark.expense_management
    def test_remove_nonexistent_expense(self, planner):
        """Тест удаления несуществующего расхода"""
        result = planner.remove_expense("non-existent-id")
        assert result is False

    # Тест 5: Установка бюджета с исключениями
    @pytest.mark.exception
    @pytest.mark.budget
    def test_set_budget_with_exceptions(self, planner):
        """Тест установки бюджета с невалидными значениями"""
        with pytest.raises(ValueError, match="Budget cannot be negative"):
            planner.set_monthly_budget(-100.0)

        with pytest.raises(ValueError, match="Budget cannot be negative"):
            planner.set_category_budget(Category.FOOD, -50.0)

    # Тест 6: Data-driven тест для расчета общей суммы расходов
    @pytest.mark.parametrize("expenses_data,expected_total", [
        ([
             ("Lunch", 25.0, Category.FOOD),
             ("Bus", 5.0, Category.TRANSPORT)
         ], 30.0),
        ([
             ("Movie", 15.0, Category.ENTERTAINMENT),
             ("Coffee", 8.0, Category.FOOD),
             ("Book", 20.0, Category.EDUCATION)
         ], 43.0),
        ([], 0.0)
    ])
    @pytest.mark.calculation
    @pytest.mark.data_driven
    def test_get_total_expenses_parametrized(self, planner, expenses_data, expected_total):
        """Параметризованный тест расчета общей суммы расходов"""
        today = date.today()

        for desc, amount, category in expenses_data:
            planner.add_expense(desc, amount, category, today)

        total = planner.get_total_expenses(today, today)
        assert total == expected_total

    # Тест 7: Расчет оставшегося месячного бюджета (исправленный)
    def get_remaining_monthly_budget(self, year: int, month: int) -> float:
        """
        Расчет оставшегося бюджета на месяц
        """
        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12")

        # Правильный расчет последнего дня месяца
        if month == 12:
            end_date = date(year, 12, 31)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        start_date = date(year, month, 1)

        total_expenses = self.get_total_expenses(start_date, end_date)
        return self._monthly_budget - total_expenses

    # Тест 8: Проверка превышения бюджета категории
    @pytest.mark.budget
    @pytest.mark.category
    def test_category_budget_exceeded(self, planner):
        """Тест проверки превышения бюджета категории"""
        planner.set_category_budget(Category.FOOD, 100.0)

        planner.add_expense("Groceries", 80.0, Category.FOOD, date.today())
        assert not planner.is_category_budget_exceeded(Category.FOOD)

        planner.add_expense("Restaurant", 30.0, Category.FOOD, date.today())
        assert planner.is_category_budget_exceeded(Category.FOOD)

    # Тест 9: Получение статистики по категориям
    @pytest.mark.statistics
    @pytest.mark.category
    def test_category_statistics(self, planner):
        """Тест получения статистики по категориям"""
        today = date.today()

        planner.add_expense("Lunch", 25.0, Category.FOOD, today)
        planner.add_expense("Dinner", 35.0, Category.FOOD, today)
        planner.add_expense("Bus", 5.0, Category.TRANSPORT, today)

        stats = planner.get_category_statistics(today, today)

        assert stats[Category.FOOD] == 60.0
        assert stats[Category.TRANSPORT] == 5.0
        assert Category.ENTERTAINMENT not in stats

    # Тест 10: Поиск самых крупных расходов
    @pytest.mark.expense_management
    @pytest.mark.sorting
    def test_top_expenses(self, planner):
        """Тест поиска самых крупных расходов"""
        planner.add_expense("Small", 10.0, Category.OTHER, date.today())
        planner.add_expense("Large", 100.0, Category.OTHER, date.today())
        planner.add_expense("Medium", 50.0, Category.OTHER, date.today())

        top_expenses = planner.get_top_expenses(2)

        assert len(top_expenses) == 2
        assert top_expenses[0].amount == 100.0
        assert top_expenses[1].amount == 50.0

    # Тест 11: Исключения при работе с датами
    @pytest.mark.exception
    @pytest.mark.calculation
    def test_get_total_expenses_invalid_dates(self, planner):
        """Тест исключений при невалидных датах"""
        today = date.today()
        yesterday = today - timedelta(days=1)

        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            planner.get_total_expenses(today, yesterday)

    # Тест 12: Data-driven тест для бюджетов категорий
    @pytest.mark.parametrize("category,budget,expenses_amount,expected_exceeded", [
        (Category.FOOD, 500.0, 450.0, False),
        (Category.ENTERTAINMENT, 200.0, 250.0, True),
        (Category.TRANSPORT, 100.0, 100.0, False),
        (Category.UTILITIES, 300.0, 0.0, False)
    ])
    @pytest.mark.budget
    @pytest.mark.data_driven
    @pytest.mark.category
    def test_category_budget_scenarios(self, planner, category, budget, expenses_amount, expected_exceeded):
        """Параметризованный тест сценариев бюджета категорий"""
        planner.set_category_budget(category, budget)

        if expenses_amount > 0:
            planner.add_expense("Test expense", expenses_amount, category, date.today())

        assert planner.is_category_budget_exceeded(category) == expected_exceeded

    # Тест 13: Получение сводки расходов
    @pytest.mark.statistics
    @pytest.mark.basic
    def test_expenses_summary(self, planner):
        """Тест получения сводки по расходам"""
        planner.set_monthly_budget(1500.0)
        planner.set_category_budget(Category.FOOD, 300.0)

        planner.add_expense("Test1", 100.0, Category.FOOD, date.today())
        planner.add_expense("Test2", 200.0, Category.TRANSPORT, date.today())

        summary = planner.get_expenses_summary()

        assert summary["total_expenses"] == 300.0
        assert summary["expense_count"] == 2
        assert summary["monthly_budget"] == 1500.0
        assert summary["category_budgets"][Category.FOOD] == 300.0


# Дополнительные тесты для класса Expense
class TestExpense:
    """Тесты для класса Expense"""

    @pytest.mark.basic
    def test_expense_creation(self):
        """Тест создания объекта расхода"""
        expense = Expense("Test", 100.0, Category.FOOD, date.today())

        assert expense.description == "Test"
        assert expense.amount == 100.0
        assert expense.category == Category.FOOD
        assert expense.date == date.today()
        assert expense.id is not None

    @pytest.mark.exception
    def test_expense_invalid_creation(self):
        """Тест создания расхода с невалидными данными"""
        with pytest.raises(ValueError):
            Expense("", 100.0, Category.FOOD, date.today())

        with pytest.raises(ValueError):
            Expense("Test", -50.0, Category.FOOD, date.today())