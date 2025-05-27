package com.ds.repositories;

import org.springframework.data.jpa.repository.JpaRepository;

import com.ds.models.Product;

public interface ProductRepository extends JpaRepository <Product,Long>{

}
