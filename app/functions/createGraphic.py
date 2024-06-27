import matplotlib.pyplot as plt
import numpy_financial as npf
import io
import base64

def create_loan_graphic(principal_amount, annual_interest_rate):
    # Calculating monthly payments for loan terms from 1 to 30 years
    loan_terms_years = range(1, 31)
    monthly_payments = [
        npf.pmt(annual_interest_rate / 12, years * 12, -principal_amount)
        for years in loan_terms_years
    ]

    # Creating a visually appealing plot
    plt.figure(figsize=(16, 9))
    plt.plot(loan_terms_years, monthly_payments, marker='o', color='#007ACC', linestyle='-', linewidth=2, markersize=6)
    plt.title('Monthly Payments', fontsize=16, fontweight='bold')
    plt.xlabel('Loan Term (Years)', fontsize=14)
    plt.ylabel('Monthly Payment ($)', fontsize=14)
    plt.xticks(range(1, 31, 1), fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(color='gray', linestyle='--', linewidth=0.5)
    plt.tight_layout()

    # Adjusting axis limits to ensure annotations fit within the plot
    max_payment = max(monthly_payments)
    plt.xlim(0, 35)
    plt.ylim(0, max_payment * 1.5)

    # Annotating the monthly payment values
    for i, payment in enumerate(monthly_payments):
        plt.annotate(f"${payment:,.2f}",
                     (loan_terms_years[i], payment),
                     textcoords="offset points",
                     xytext=(0,10),
                     ha='left',
                     fontsize=16,
                     rotation=50,
                     weight='bold',
                     backgroundcolor=(0,0,0,0.35),
                     color='black')

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Encode the BytesIO object in base64
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')

    # Display the plot (optional, can be commented out if not needed)
    # plt.show()

    # Return the base64 string
    return image_base64

