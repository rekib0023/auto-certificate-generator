module.exports = (sequelize, DataTypes) => {
  const Campaign = sequelize.define("Campaign", {
    campaign_name: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    company_name: {
      type: DataTypes.STRING,
      allowNull: false,
      unique: true,
    },
    created_by: {
      type: DataTypes.INTEGER,
      allowNull: false,
    },
  });

  return Campaign
};
