package edu.nd.dronology.services.core.items;

import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class UAVRegistration implements IUAVRegistration {

	private String id;
	private String name;
	private String description;
	private String type = "Default";
	private Map<String, Serializable> attributes;
	private byte[] image;

	public UAVRegistration() {
		id = UUID.randomUUID().toString();
		attributes = new HashMap<>();
	}

	@Override
	public String getName() {
		// TODO Auto-generated method stub
		return name;
	}

	@Override
	public void setName(String name) {
		this.name = name;
	}

	@Override
	public String getId() {
		return id;
	}

	@Override
	public String getDescription() {
		return description;
	}

	@Override
	public void setType(String type) {
		this.type = type;

	}

	@Override
	public void setDescription(String description) {
		this.description = description;

	}

	@Override
	public String getType() {
		return type;
	}

	@Override
	public Serializable getAttribute(String key) {
		return attributes.get(key);
	}

	@Override
	public void addAttribute(String key, Serializable value) {
		attributes.put(key, value);
	}

	@Override
	public void setUAVImage(byte[] image) {
		this.image = image;
	}

	@Override
	public byte[] getImage() {
		return image;
	}
}
