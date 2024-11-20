fn addition(num: i32) -> i32 {
    let mut sum = num;
    for i in 1..5 {
        sum += i;
    }

    return sum;
}

fn condition(num: i32) -> i32 {
  let counter = num + 10;
  if counter > 10 {
    return 10;
  } else {
    return counter;
  }
}

fn main() {
    let num = 15;
    println!("The addition of {} is {}", num, addition(num));
    println!("Condition {}", condition(num));
}