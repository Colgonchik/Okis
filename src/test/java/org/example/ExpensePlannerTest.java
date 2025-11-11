package org.example;

import org.testng.annotations.*;
import static org.testng.Assert.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

public class ExpensePlannerTest {
    private ExpensePlanner planner;

    @BeforeClass(groups = "setup")
    public void setUpClass() {
        System.out.println("Starting Expense Planner tests...");
    }

    @AfterClass(groups = "setup")
    public void tearDownClass() {
        System.out.println("Finished Expense Planner tests...");
    }

    @BeforeMethod(groups = "setup")
    public void setUp() {
        planner = new ExpensePlanner();
    }

    @AfterMethod(groups = "setup")
    public void tearDown() {
        planner = null;
    }

    // Тест 1: Добавление валидного расхода
    @Test(groups = {"expense-management", "basic"})
    public void testAddValidExpense() {
        planner.addExpense("Lunch", 25.50, ExpensePlanner.Category.FOOD, LocalDate.now());
        assertEquals(planner.getAllExpenses().size(), 1);

        ExpensePlanner.Expense expense = planner.getAllExpenses().get(0);
        assertEquals(expense.getDescription(), "Lunch");
        assertEquals(expense.getAmount(), 25.50);
        assertEquals(expense.getCategory(), ExpensePlanner.Category.FOOD);
    }

    // Тест 2: Добавление расхода с невалидными данными (исключение)
    @Test(groups = {"exceptions", "expense-management"},
            expectedExceptions = IllegalArgumentException.class)
    public void testAddExpenseWithEmptyDescription() {
        planner.addExpense("", 25.50, ExpensePlanner.Category.FOOD, LocalDate.now());
    }

    // Тест 3: Добавление расхода с отрицательной суммой (исключение)
    @Test(groups = {"exceptions", "expense-management"},
            expectedExceptions = IllegalArgumentException.class)
    public void testAddExpenseWithNegativeAmount() {
        planner.addExpense("Test", -10.0, ExpensePlanner.Category.FOOD, LocalDate.now());
    }

    // Тест 4: Удаление существующего расхода
    @Test(groups = {"expense-management", "basic"})
    public void testRemoveExistingExpense() {
        planner.addExpense("To remove", 15.0, ExpensePlanner.Category.OTHER, LocalDate.now());
        String expenseId = planner.getAllExpenses().get(0).getId();

        assertTrue(planner.removeExpense(expenseId));
        assertEquals(planner.getAllExpenses().size(), 0);
    }

    // Тест 5: Удаление несуществующего расхода
    @Test(groups = {"expense-management"})
    public void testRemoveNonExistingExpense() {
        assertFalse(planner.removeExpense("non-existing-id"));
    }

    // Тест 6: DataProvider для тестирования общей суммы расходов
    @DataProvider(name = "expenseSumData")
    public Object[][] provideExpenseSumData() {
        return new Object[][] {
                {new Object[][]{
                        {"Lunch", 25.0, ExpensePlanner.Category.FOOD},
                        {"Bus", 5.0, ExpensePlanner.Category.TRANSPORT}
                }, 30.0},
                {new Object[][]{
                        {"Movie", 15.0, ExpensePlanner.Category.ENTERTAINMENT},
                        {"Coffee", 8.0, ExpensePlanner.Category.FOOD},
                        {"Book", 20.0, ExpensePlanner.Category.EDUCATION}
                }, 43.0},
                {new Object[][]{}, 0.0}
        };
    }

    @Test(groups = {"calculations", "data-driven"}, dataProvider = "expenseSumData")
    public void testGetTotalExpenses(Object[][] expensesData, double expectedTotal) {
        LocalDate today = LocalDate.now();

        for (Object[] expenseData : expensesData) {
            planner.addExpense(
                    (String) expenseData[0],
                    (Double) expenseData[1],
                    (ExpensePlanner.Category) expenseData[2],
                    today
            );
        }

        double total = planner.getTotalExpenses(today, today);
        assertEquals(total, expectedTotal, 0.001);
    }

    // Тест 7: Расчет оставшегося месячного бюджета
    @Test(groups = {"budget", "calculations"})
    public void testRemainingMonthlyBudget() {
        planner.setMonthlyBudget(1000.0);
        LocalDate firstOfMonth = LocalDate.now().withDayOfMonth(1);

        planner.addExpense("Rent", 500.0, ExpensePlanner.Category.UTILITIES, firstOfMonth);
        planner.addExpense("Food", 200.0, ExpensePlanner.Category.FOOD, firstOfMonth);

        double remaining = planner.getRemainingMonthlyBudget(
                firstOfMonth.getYear(),
                firstOfMonth.getMonthValue()
        );

        assertEquals(remaining, 300.0, 0.001);
    }

    // Тест 8: Проверка превышения бюджета категории
    @Test(groups = {"budget", "category"})
    public void testCategoryBudgetExceeded() {
        planner.setCategoryBudget(ExpensePlanner.Category.FOOD, 100.0);

        planner.addExpense("Groceries", 80.0, ExpensePlanner.Category.FOOD, LocalDate.now());
        assertFalse(planner.isCategoryBudgetExceeded(ExpensePlanner.Category.FOOD));

        planner.addExpense("Restaurant", 30.0, ExpensePlanner.Category.FOOD, LocalDate.now());
        assertTrue(planner.isCategoryBudgetExceeded(ExpensePlanner.Category.FOOD));
    }

    // Тест 9: Получение статистики по категориям
    @Test(groups = {"statistics", "category"})
    public void testCategoryStatistics() {
        LocalDate today = LocalDate.now();

        planner.addExpense("Lunch", 25.0, ExpensePlanner.Category.FOOD, today);
        planner.addExpense("Dinner", 35.0, ExpensePlanner.Category.FOOD, today);
        planner.addExpense("Bus", 5.0, ExpensePlanner.Category.TRANSPORT, today);

        Map<ExpensePlanner.Category, Double> stats = planner.getCategoryStatistics(today, today);

        assertEquals(stats.get(ExpensePlanner.Category.FOOD), 60.0, 0.001);
        assertEquals(stats.get(ExpensePlanner.Category.TRANSPORT), 5.0, 0.001);
        assertNull(stats.get(ExpensePlanner.Category.ENTERTAINMENT));
    }

    // Тест 10: Поиск самых крупных расходов
    @Test(groups = {"expense-management", "sorting"})
    public void testTopExpenses() {
        planner.addExpense("Small", 10.0, ExpensePlanner.Category.OTHER, LocalDate.now());
        planner.addExpense("Large", 100.0, ExpensePlanner.Category.OTHER, LocalDate.now());
        planner.addExpense("Medium", 50.0, ExpensePlanner.Category.OTHER, LocalDate.now());

        List<ExpensePlanner.Expense> topExpenses = planner.getTopExpenses(2);

        assertEquals(topExpenses.size(), 2);
        assertEquals(topExpenses.get(0).getAmount(), 100.0, 0.001);
        assertEquals(topExpenses.get(1).getAmount(), 50.0, 0.001);
    }

    // Тест 11: Исключение при невалидных датах
    @Test(groups = {"exceptions", "calculations"},
            expectedExceptions = IllegalArgumentException.class)
    public void testGetTotalExpensesWithInvalidDates() {
        planner.getTotalExpenses(LocalDate.now().plusDays(1), LocalDate.now());
    }

    // Тест 12: DataProvider для тестирования бюджета категорий
    @DataProvider(name = "categoryBudgetData")
    public Object[][] provideCategoryBudgetData() {
        return new Object[][] {
                {ExpensePlanner.Category.FOOD, 500.0, 450.0, false},
                {ExpensePlanner.Category.ENTERTAINMENT, 200.0, 250.0, true},
                {ExpensePlanner.Category.TRANSPORT, 100.0, 100.0, false},
                {ExpensePlanner.Category.UTILITIES, 300.0, 0.0, false}
        };
    }

    @Test(groups = {"budget", "data-driven", "category"}, dataProvider = "categoryBudgetData")
    public void testCategoryBudgetScenarios(ExpensePlanner.Category category,
                                            double budget,
                                            double expenses,
                                            boolean expectedExceeded) {
        planner.setCategoryBudget(category, budget);

        if (expenses > 0) {
            planner.addExpense("Test expense", expenses, category, LocalDate.now());
        }

        assertEquals(planner.isCategoryBudgetExceeded(category), expectedExceeded);
    }

    // Тест 13: Установка отрицательного бюджета (исключение)
    @Test(groups = {"exceptions", "budget"},
            expectedExceptions = IllegalArgumentException.class)
    public void testSetNegativeMonthlyBudget() {
        planner.setMonthlyBudget(-100.0);
    }

    // Тест 14: Получение расходов по несуществующей категории
    @Test(groups = {"exceptions", "category"},
            expectedExceptions = IllegalArgumentException.class)
    public void testGetExpensesByNullCategory() {
        planner.getExpensesByCategory(null);
    }
}
