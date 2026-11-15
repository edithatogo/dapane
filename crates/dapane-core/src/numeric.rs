use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Signed, Zero};

use crate::{DapaneError, ExactNumber, Rational};

pub(crate) const MAX_NUMERIC_DIGITS: usize = 96;
pub(crate) const MAX_DECIMAL_SCALE: usize = 36;
pub(crate) const MAX_INTERMEDIATE_BITS: u64 = 4096;

fn unsigned_integer(value: &str, path: &str) -> Result<BigInt, DapaneError> {
    if value.is_empty() || !value.bytes().all(|v| v.is_ascii_digit()) {
        return Err(DapaneError::new(
            "invalid_number",
            "Expected unsigned decimal digits without signs or whitespace",
            path,
        ));
    }
    if value.len() > MAX_NUMERIC_DIGITS {
        return Err(DapaneError::new(
            "precision_limit",
            "Numeric input exceeds 96 digits",
            path,
        ));
    }
    BigInt::parse_bytes(value.as_bytes(), 10)
        .ok_or_else(|| DapaneError::new("invalid_number", "Invalid integer", path))
}

pub(crate) fn parse(value: &ExactNumber, path: &str) -> Result<BigRational, DapaneError> {
    match value {
        ExactNumber::Decimal(value) => {
            let mut parts = value.split('.');
            let whole = parts.next().unwrap_or("");
            let fraction = parts.next();
            if parts.next().is_some() {
                return Err(DapaneError::new(
                    "invalid_number",
                    "Only one decimal point is allowed",
                    path,
                ));
            }
            unsigned_integer(whole, path)?;
            match fraction {
                Some(fraction) => {
                    unsigned_integer(fraction, path)?;
                    if fraction.len() > MAX_DECIMAL_SCALE
                        || whole.len() + fraction.len() > MAX_NUMERIC_DIGITS
                    {
                        return Err(DapaneError::new(
                            "precision_limit",
                            "Decimal exceeds 96 digits or scale 36",
                            path,
                        ));
                    }
                    let coefficient = unsigned_integer(&format!("{whole}{fraction}"), path)?;
                    Ok(BigRational::new(coefficient, ten_pow(fraction.len() as u8)))
                }
                None => Ok(BigRational::from_integer(unsigned_integer(whole, path)?)),
            }
        }
        ExactNumber::Rational(value) => {
            let numerator = unsigned_integer(&value.numerator, &format!("{path}/numerator"))?;
            let denominator = unsigned_integer(&value.denominator, &format!("{path}/denominator"))?;
            if denominator.is_zero() {
                return Err(DapaneError::new(
                    "zero_denominator",
                    "Rational denominator must be positive",
                    &format!("{path}/denominator"),
                ));
            }
            Ok(BigRational::new(numerator, denominator))
        }
    }
}

pub(crate) fn bounded(value: BigRational, path: &str) -> Result<BigRational, DapaneError> {
    if value.numer().bits() > MAX_INTERMEDIATE_BITS || value.denom().bits() > MAX_INTERMEDIATE_BITS
    {
        Err(DapaneError::new(
            "precision_limit",
            "Intermediate rational exceeds 4096 bits",
            path,
        ))
    } else {
        Ok(value)
    }
}

pub(crate) fn wire(value: &BigRational) -> Rational {
    Rational {
        numerator: value.numer().to_string(),
        denominator: value.denom().to_string(),
    }
}

pub(crate) fn ten_pow(scale: u8) -> BigInt {
    BigInt::from(10).pow(u32::from(scale))
}

pub(crate) fn rounded_minor(value: &BigRational, scale: u8) -> BigInt {
    // Evaluated source values are nonnegative; the remainder is therefore nonnegative.
    let numerator = value.numer() * ten_pow(scale);
    let mut quotient = &numerator / value.denom();
    let remainder = &numerator % value.denom();
    let twice_remainder = remainder * 2;
    if twice_remainder > *value.denom()
        || (twice_remainder == *value.denom() && (&quotient % 2u8) == BigInt::one())
    {
        quotient += 1;
    }
    quotient
}

pub(crate) fn from_minor(value: &BigInt, scale: u8) -> BigRational {
    BigRational::new(value.clone(), ten_pow(scale))
}

pub(crate) fn format_minor(value: &BigInt, scale: u8) -> String {
    if scale == 0 {
        return value.to_string();
    }
    let digits = value.abs().to_string();
    let width = usize::from(scale) + 1;
    let padded = format!("{digits:0>width$}");
    let point = padded.len() - usize::from(scale);
    let sign = if value.is_negative() { "-" } else { "" };
    format!("{sign}{}.{}", &padded[..point], &padded[point..])
}
