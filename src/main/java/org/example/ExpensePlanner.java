package org.example;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

public class ExpensePlanner {
    private final List<Expense> expenses;
    private final Map<String, Double> categoryBudgets;
    private double monthlyBudget;

    public enum Category {
        FOOD, TRANSPORT, ENTERTAINMENT, UTILITIES, HEALTH, EDUCATION, OTHER
    }

    public static class Expense {
        private final String id;
        private final String description;
        private final double amount;
        private final Category category;
        private final LocalDate date;

        public Expense(String description, double amount, Category category, LocalDate date) {
            this.id = UUID.randomUUID().toString();
            this.description = description;
            this.amount = amount;
            this.category = category;
            this.date = date;
        }

        // Getters
        public String getId() { return id; }
        public String getDescription() { return description; }
        public double getAmount() { return amount; }
        public Category getCategory() { return category; }
        public LocalDate getDate() { return date; }
    }

    public ExpensePlanner() {
        this.expenses = new ArrayList<>();
        this.categoryBudgets = new HashMap<>();
        this.monthlyBudget = 0.0;
        initializeCategoryBudgets();
    }

    private void initializeCategoryBudgets() {
        for (Category category : Category.values()) {
            categoryBudgets.put(category.name(), 0.0);
        }
    }

    /**
     * 1. Добавление расхода
     */
    public void addExpense(String description, double amount, Category category, LocalDate date) {
        if (description == null || description.trim().isEmpty()) {
            throw new IllegalArgumentException("Description cannot be empty");
        }
        if (amount <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
        if (category == null) {
            throw new IllegalArgumentException("Category cannot be null");
        }
        if (date == null || date.isAfter(LocalDate.now())) {
            throw new IllegalArgumentException("Date cannot be in the future");
        }

        Expense expense = new Expense(description.trim(), amount, category, date);
        expenses.add(expense);
    }

    /**
     * 2. Удаление расхода по ID
     */
    public boolean removeExpense(String expenseId) {
        if (expenseId == null || expenseId.trim().isEmpty()) {
            throw new IllegalArgumentException("Expense ID cannot be empty");
        }

        return expenses.removeIf(expense -> expense.getId().equals(expenseId));
    }

    /**
     * 3. Установка месячного бюджета
     */
    public void setMonthlyBudget(double budget) {
        if (budget < 0) {
            throw new IllegalArgumentException("Budget cannot be negative");
        }
        this.monthlyBudget = budget;
    }

    /**
     * 4. Установка бюджета для категории
     */
    public void setCategoryBudget(Category category, double budget) {
        if (category == null) {
            throw new IllegalArgumentException("Category cannot be null");
        }
        if (budget < 0) {
            throw new IllegalArgumentException("Budget cannot be negative");
        }

        categoryBudgets.put(category.name(), budget);
    }

    /**
     * 5. Получение общей суммы расходов за период
     */
    public double getTotalExpenses(LocalDate startDate, LocalDate endDate) {
        if (startDate == null || endDate == null) {
            throw new IllegalArgumentException("Dates cannot be null");
        }
        if (startDate.isAfter(endDate)) {
            throw new IllegalArgumentException("Start date cannot be after end date");
        }

        return expenses.stream()
                .filter(expense -> !expense.getDate().isBefore(startDate) &&
                        !expense.getDate().isAfter(endDate))
                .mapToDouble(Expense::getAmount)
                .sum();
    }

    /**
     * 6. Получение расходов по категории
     */
    public List<Expense> getExpensesByCategory(Category category) {
        if (category == null) {
            throw new IllegalArgumentException("Category cannot be null");
        }

        return expenses.stream()
                .filter(expense -> expense.getCategory() == category)
                .collect(Collectors.toList());
    }

    /**
     * 7. Расчет оставшегося бюджета на месяц
     */
    public double getRemainingMonthlyBudget(int year, int month) {
        if (month < 1 || month > 12) {
            throw new IllegalArgumentException("Month must be between 1 and 12");
        }

        LocalDate startDate = LocalDate.of(year, month, 1);
        LocalDate endDate = startDate.withDayOfMonth(startDate.lengthOfMonth());

        double totalExpenses = getTotalExpenses(startDate, endDate);
        return monthlyBudget - totalExpenses;
    }

    /**
     * 8. Проверка превышения бюджета категории
     */
    public boolean isCategoryBudgetExceeded(Category category) {
        if (category == null) {
            throw new IllegalArgumentException("Category cannot be null");
        }

        double categoryBudget = categoryBudgets.get(category.name());
        if (categoryBudget == 0) return false;

        double categoryExpenses = getExpensesByCategory(category).stream()
                .mapToDouble(Expense::getAmount)
                .sum();

        return categoryExpenses > categoryBudget;
    }

    /**
     * 9. Получение статистики по категориям
     */
    public Map<Category, Double> getCategoryStatistics(LocalDate startDate, LocalDate endDate) {
        if (startDate == null || endDate == null) {
            throw new IllegalArgumentException("Dates cannot be null");
        }

        return expenses.stream()
                .filter(expense -> !expense.getDate().isBefore(startDate) &&
                        !expense.getDate().isAfter(endDate))
                .collect(Collectors.groupingBy(
                        Expense::getCategory,
                        Collectors.summingDouble(Expense::getAmount)
                ));
    }

    /**
     * 10. Поиск самых крупных расходов
     */
    public List<Expense> getTopExpenses(int limit) {
        if (limit <= 0) {
            throw new IllegalArgumentException("Limit must be positive");
        }

        return expenses.stream()
                .sorted((e1, e2) -> Double.compare(e2.getAmount(), e1.getAmount()))
                .limit(limit)
                .collect(Collectors.toList());
    }

    // Getters
    public List<Expense> getAllExpenses() {
        return new ArrayList<>(expenses);
    }

    public double getMonthlyBudget() {
        return monthlyBudget;
    }

    public double getCategoryBudget(Category category) {
        return categoryBudgets.get(category.name());
    }
}